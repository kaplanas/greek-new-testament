echo "WITH relations_to_check AS
           (SELECT relations.SentenceID, relations.Relation, relations.HeadPos,
                   relations.DependentPos, relations.FirstPos,
                   relations.LastPos,
                   CASE WHEN checked_relation_tokens.Relation IS NULL
                             THEN checked_relation_types.CheckOrder
                        ELSE -1
                   END AS CheckOrder
            FROM gnt.relations
                 LEFT JOIN gnt.checked_relation_types
                 ON relations.Relation = checked_relation_types.Relation
                 LEFT JOIN gnt.checked_relation_tokens
                 ON relations.SentenceID = checked_relation_tokens.SentenceID
                    AND relations.HeadPos = checked_relation_tokens.HeadPos
                    AND relations.DependentPos = checked_relation_tokens.DependentPos
            WHERE (checked_relation_types.Relation IS NOT NULL
                   AND checked_relation_tokens.SentenceID IS NULL)
                  OR relations.Relation <> checked_relation_tokens.Relation),
           shortest_strings AS
           (SELECT strings.SentenceID, relations_to_check.HeadPos,
                   relations_to_check.DependentPos, relations_to_check.FirstPos,
                   relations_to_check.LastPos, relations_to_check.Relation,
                   relations_to_check.CheckOrder, MAX(strings.Start) AS Start,
                   MIN(strings.Stop) AS Stop
            FROM gnt.strings
                 JOIN relations_to_check
                 ON strings.SentenceID = relations_to_check.SentenceID
                    AND FirstPos >= Start
                    AND FirstPos <= Stop
                    AND LastPos >= Start
                    AND LastPos <= Stop
            GROUP BY strings.SentenceID, relations_to_check.HeadPos,
                     relations_to_check.DependentPos,
                     relations_to_check.FirstPos, relations_to_check.LastPos,
                     relations_to_check.Relation,
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
                                    shortest_strings.FirstPos - strings.Start),
                    IF(shortest_strings.FirstPos > strings.Start, ' ', ''),
                    IF(shortest_strings.HeadPos < shortest_strings.DependentPos,
                       'H', 'D'),
                    IF(shortest_strings.FirstPos > strings.Start,
                       SUBSTRING_INDEX(SUBSTRING_INDEX(strings.String, ' ',
                                                       shortest_strings.FirstPos -
                                                       strings.Start + 1),
                                           ' ', -1),
                       SUBSTRING_INDEX(strings.String, ' ',
                                       shortest_strings.FirstPos -
                                       strings.Start + 1)),
                    IF(shortest_strings.HeadPos < shortest_strings.DependentPos,
                       'h', 'd'),
                    IF(shortest_strings.LastPos - shortest_strings.FirstPos > 1,
                       CONCAT(' ',
                              SUBSTRING_INDEX(SUBSTRING_INDEX(strings.String,
                                                              ' ',
                                                              shortest_strings.LastPos -
                                                              strings.Start),
                                              ' ',
                                              1 - (shortest_strings.LastPos -
                                                   shortest_strings.FirstPos))),
                       ''),
                    ' ',
                    IF(shortest_strings.HeadPos < shortest_strings.DependentPos,
                       'D', 'H'),
                    IF(strings.Stop > shortest_strings.LastPos,
                       SUBSTRING_INDEX(SUBSTRING_INDEX(strings.String, ' ',
                                                       -1 -
                                                       (strings.Stop -
                                                        shortest_strings.LastPos)),
                                       ' ', 1),
                       SUBSTRING_INDEX(strings.String, ' ',
                                       -1 - (strings.Stop -
                                             shortest_strings.LastPos))),
                    IF(shortest_strings.HeadPos < shortest_strings.DependentPos,
                       'd', 'h'),
                    IF(strings.Stop > shortest_strings.LastPos, ' ', ''),
                    SUBSTRING_INDEX(strings.String, ' ',
                                    0 - (strings.Stop -
                                         shortest_strings.LastPos))) AS String,
             shortest_strings.SentenceID, shortest_strings.HeadPos,
             shortest_strings.DependentPos, shortest_strings.Relation
      FROM gnt.strings
           JOIN shortest_strings
           ON strings.SentenceID = shortest_strings.SentenceID
              AND strings.Start = shortest_strings.Start
              AND strings.Stop = shortest_strings.Stop
           JOIN book_chapter_verse
           ON strings.SentenceID = book_chapter_verse.SentenceID
      ORDER BY shortest_strings.CheckOrder, book_chapter_verse.Book,
               book_chapter_verse.Chapter, book_chapter_verse.Verse,
               shortest_strings.HeadPos, shortest_strings.DependentPos
      LIMIT 50;" | mysql -u root -p$MYSQL_PASSWORD 2>/dev/null | while IFS=$'\t' read citation string sentence_id head_pos dependent_pos relation
do
  if [ "$citation" != "Citation" ]
  then
    colored_string=$(echo "$string" | sed ''/H/s//`printf "\e[1;35m"`/'' | sed ''/h/s//`printf "\e[0m"`/'' | sed ''/D/s//`printf "\e[1;36m"`/'' | sed ''/d/s//`printf "\e[0m"`/'')
    echo "$citation ($relation): $colored_string"
    read -u 1 -p "Ok? " relation_is_ok
    if [ "$relation_is_ok" == "y" ]
    then
      echo "INSERT INTO gnt.checked_relation_tokens
            (SentenceID, HeadPos, DependentPos, Relation)
            SELECT '$sentence_id', '$head_pos', '$dependent_pos', Relation
            FROM gnt.relations
            WHERE relations.SentenceID = '$sentence_id'
                  AND relations.HeadPos = '$head_pos'
                  AND relations.DependentPos = '$dependent_pos'
            ON DUPLICATE KEY UPDATE
            checked_relation_tokens.Relation = (SELECT Relation
                                                FROM gnt.relations
                                                WHERE relations.SentenceID = '$sentence_id'
                                                      AND relations.HeadPos = '$head_pos'
                                                      AND relations.DependentPos = '$dependent_pos');" | mysql -u root -p$MYSQL_PASSWORD 2>/dev/null
    else
      echo "DELETE FROM gnt.checked_relation_tokens
            WHERE SentenceID = '$sentence_id'
                  AND HeadPos = '$head_pos'
                  AND DependentPos = '$dependent_pos';" | mysql -u root -p$MYSQL_PASSWORD 2>/dev/null
    fi
    echo ""
  fi
done
