echo "WITH words_to_check AS
           (SELECT TypeName, HeadOrDep, SentenceID, SentencePosition,
                   MIN(LEAST(SentencePosition, OtherPosition)) AS FirstPos,
                   MAX(GREATEST(SentencePosition, OtherPosition)) AS LastPos,
                   CheckOrder
            FROM gnt.required_types
            GROUP BY TypeName, HeadOrDep, SentenceID, SentencePosition,
                     CheckOrder),
           relations_to_check AS
           (SELECT words_to_check.TypeName, words_to_check.SentenceID,
                   words_to_check.SentencePosition, words_to_check.FirstPos,
                   words_to_check.LastPos,
                   CASE WHEN words_to_check.TypeName = 'NominalType'
                             THEN words.NominalType
                   END AS NewType,
                   CASE WHEN words_to_check.TypeName = 'NominalType'
                             AND words.NominalType <> checked_types.NominalType
                             THEN checked_types.NominalType
                   END AS OldType,
                   words_to_check.CheckOrder
            FROM words_to_check
                 JOIN gnt.words
                 ON words_to_check.SentenceID = words.SentenceId
                    AND words_to_check.SentencePosition = words.SentencePosition
                 LEFT JOIN gnt.checked_types
                 ON words_to_check.SentenceID = checked_types.SentenceID
                    AND words_to_check.SentencePosition = checked_types.SentencePosition
            WHERE (words_to_check.TypeName = 'NominalType'
                   AND (checked_types.NominalType IS NULL
                        OR words.NominalType <> checked_types.NominalType))),
           shortest_strings AS
           (SELECT relations_to_check.TypeName, strings.SentenceID,
                   relations_to_check.SentencePosition,
                   relations_to_check.NewType, relations_to_check.OldType,
                   relations_to_check.CheckOrder, MAX(strings.Start) AS Start,
                   MIN(strings.Stop) AS Stop
            FROM gnt.strings
                 JOIN relations_to_check
                 ON strings.SentenceID = relations_to_check.SentenceID
                    AND FirstPos >= Start
                    AND FirstPos <= Stop
                    AND LastPos >= Start
                    AND LastPos <= Stop
            GROUP BY relations_to_check.TypeName, strings.SentenceID,
                     relations_to_check.SentencePosition,
                     relations_to_check.NewType, relations_to_check.OldType,
                     relations_to_check.CheckOrder),
           book_chapter_verse AS
           (SELECT SentenceID,
                   CASE WHEN MIN(Book) = 'Matt' THEN 1
                        WHEN MIN(Book) = 'Mark' THEN 2
                        WHEN MIN(Book) = 'Luke' THEN 3
                        WHEN MIN(Book) = 'John' THEN 4
                        WHEN MIN(Book) = 'Acts' THEN 5
                        WHEN MIN(Book) = 'Rom' THEN 6
                        WHEN MIN(Book) = '1Cor' THEN 7
                        WHEN MIN(Book) = '2Cor' THEN 8
                        WHEN MIN(Book) = 'Gal' THEN 9
                        WHEN MIN(Book) = 'Eph' THEN 10
                        WHEN MIN(Book) = 'Phil' THEN 11
                        WHEN MIN(Book) = 'Col' THEN 12
                        WHEN MIN(Book) = '1Thess' THEN 13
                        WHEN MIN(Book) = '2Thess' THEN 14
                        WHEN MIN(Book) = '1Tim' THEN 15
                        WHEN MIN(Book) = '2Tim' THEN 16
                        WHEN MIN(Book) = 'Titus' THEN 17
                        WHEN MIN(Book) = 'Phlm' THEN 18
                        WHEN MIN(Book) = 'Heb' THEN 19
                        WHEN MIN(Book) = 'Jas' THEN 20
                        WHEN MIN(Book) = '1Pet' THEN 21
                        WHEN MIN(Book) = '2Pet' THEN 22
                        WHEN MIN(Book) = '1John' THEN 23
                        WHEN MIN(Book) = '2John' THEN 24
                        WHEN MIN(Book) = '3John' THEN 25
                        WHEN MIN(Book) = 'Jude' THEN 26
                        WHEN MIN(Book) = 'Rev' THEN 27
                        ELSE -1
                   END AS Book, MIN(Chapter) AS Chapter, MIN(Verse) AS Verse
            FROM gnt.words
            GROUP BY SentenceID)
      SELECT strings.Citation,
             CONCAT(SUBSTRING_INDEX(strings.String, ' ',
                                    shortest_strings.SentencePosition -
                                    strings.Start),
                    IF(shortest_strings.SentencePosition > strings.Start, ' ',
                       ''),
                    'H',
                    IF(shortest_strings.SentencePosition > strings.Start,
                       SUBSTRING_INDEX(SUBSTRING_INDEX(strings.String, ' ',
                                                       shortest_strings.SentencePosition -
                                                       strings.Start + 1),
                                           ' ', -1),
                       SUBSTRING_INDEX(strings.String, ' ',
                                       shortest_strings.SentencePosition -
                                       strings.Start + 1)),
                    'h',
                    IF(strings.Stop > shortest_strings.SentencePosition, ' ', ''),
                    SUBSTRING_INDEX(strings.String, ' ',
                                    0 - (strings.Stop -
                                         shortest_strings.SentencePosition))) AS String,
             shortest_strings.TypeName, shortest_strings.SentenceID,
             shortest_strings.SentencePosition, shortest_strings.NewType,
             shortest_strings.OldType, shortest_strings.CheckOrder
      FROM gnt.strings
           JOIN shortest_strings
           ON strings.SentenceID = shortest_strings.SentenceID
              AND strings.Start = shortest_strings.Start
              AND strings.Stop = shortest_strings.Stop
           JOIN book_chapter_verse
           ON strings.SentenceID = book_chapter_verse.SentenceID
      ORDER BY shortest_strings.CheckOrder, book_chapter_verse.Book,
               book_chapter_verse.Chapter, book_chapter_verse.Verse,
               shortest_strings.SentencePosition
      LIMIT 50;" | mysql -u root -p$MYSQL_PASSWORD 2>/dev/null | while IFS=$'\t' read citation string type_name sentence_id sentence_pos new_type old_type check_order
do
  if [ "$citation" != "Citation" ]
  then
    colored_string=$(echo "$string" | sed ''/H/s//`printf "\e[1;35m"`/'' | sed ''/h/s//`printf "\e[0m"`/'')
    type_string="$type_name: $new_type"
    if [ "$old_type" != "NULL" ]
    then
      type_string="$type_name: $old_type -> $new_type"
    fi
    type_string="$type_string"
    echo "$citation ($type_string): $colored_string"
    read -u 1 -p "Ok? " type_is_ok
    if [ "$type_is_ok" == "y" ]
    then
      echo "INSERT INTO gnt.checked_types
            (SentenceID, SentencePosition, NominalType)
            VALUES
            ('$sentence_id', '$sentence_pos', '$new_type')
            ON DUPLICATE KEY UPDATE
            checked_types.NominalType = '$new_type';" | mysql -u root -p$MYSQL_PASSWORD 2>/dev/null
    else
      echo "DELETE FROM gnt.checked_types
            WHERE SentenceID = '$sentence_id'
                  AND SentencePosition = '$sentence_pos';" | mysql -u root -p$MYSQL_PASSWORD 2>/dev/null
    fi
    echo ""
  fi
done
