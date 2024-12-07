echo "WITH mixed_types AS
           (SELECT SentenceID, HeadPos
            FROM gnt.relations
            WHERE Relation IN
                  ('conjunct', 'conjunct, main', 'conjunct, subordinate',
                   'conjunct, ἤ', 'conjunct, ὅτι', 'conjunct, ὡς, clause',
                   'conjunct, ὡς, non-clause', 'conjunct, ὡς, other')
                  AND SentenceID NOT IN
                      ('Matt 7:29.1 - Matt 7:29.13',
                       'Luke 6:22.1 - Luke 6:22.25',
                       'John 6:26.1 - John 6:26.24',
                       'John 12:6.1 - John 12:6.21',
                       '1Cor 13:2.1 - 1Cor 13:2.28',
                       '1Cor 13:3.1 - 1Cor 13:3.21',
                       '2Cor 9:5.1 - 2Cor 9:5.26',
                       '2Cor 6:8.9 - 2Cor 6:10.16',
                       'Phil 4:8.1 - Phil 4:8.25',
                       'Phlm 1:15.1 - Phlm 1:16.20',
                       '1Pet 4:15.1 - 1Pet 4:15.14',
                       'Rev 14:2.1 - Rev 14:2.15')
            GROUP BY SentenceID, HeadPos
            HAVING COUNT(DISTINCT CASE WHEN Relation LIKE '%main'
                                            OR Relation LIKE '%subordinate'
                                            OR Relation LIKE '% clause'
                                            THEN 'main/sub'
                                       ELSE Relation
                                  END) > 1),
           no_subs AS
           (SELECT SentenceID, HeadPos
            FROM gnt.relations
            WHERE Relation IN ('conjunct, main', 'conjunct, subordinate',
                               'conjunct, ὡς, clause')
            GROUP BY SentenceID, HeadPos
            HAVING SUM(CASE WHEN Relation = 'conjunct, main'
                                 THEN 1
                       END) > 0
                   AND SUM(CASE WHEN Relation <> 'conjunct, main'
                                     THEN 1
                           END) = 0),
           duplicates AS
           (SELECT SentenceID, HeadPos
            FROM gnt.relations
            WHERE Relation IN
                  ('conjunct, chain', 'conjunct, main',
                   'conjunct, subordinate', 'conjunct, ἤ',
                   'conjunct, μέν δέ', 'conjunct, ὅτι',
                   'conjunct, ὡς, clause', 'conjunct, ὡς, non-clause',
                   'conjunct, ὡς, other')
                  AND SentenceID NOT IN
                      ('2Cor 6:8.9 - 2Cor 6:10.16')
            GROUP BY SentenceID, HeadPos, Relation
            HAVING COUNT(*) > 1),
           no_deps AS
           (SELECT words.SentenceID, SentencePosition AS DependentPos
            FROM gnt.words
                 LEFT JOIN gnt.relations
                 ON words.SentenceID = relations.SentenceID
                    AND words.SentencePosition = relations.HeadPos
                    AND relations.Relation LIKE '%conjunct%'
                 LEFT JOIN gnt.relations spc
                 ON words.SentenceID = spc.SentenceID
                    AND words.SentencePosition = spc.DependentPos
                    AND spc.Relation = 'second-position clitic'
            WHERE words.POS = 'conj'
                  AND relations.Relation <> 'adv'
                  AND relations.SentenceID IS NULL
                  AND spc.SentenceID IS NULL),
           all_heads AS
           (SELECT SentenceID, HeadPos
            FROM mixed_types
            UNION
            SELECT SentenceID, HeadPos
            FROM no_subs
            UNION
            SELECT SentenceID, HeadPos
            FROM duplicates),
           relations_to_check AS
           (SELECT SentenceID, HeadPos, DependentPos, FirstPos, LastPos,
                   Relation
            FROM gnt.relations
            WHERE (SentenceID, HeadPos) IN
                  (SELECT SentenceID, HeadPos
                   FROM all_heads)
                  OR (SentenceID, DependentPos) IN
                     (SELECT SentenceID, DependentPos
                      FROM no_deps)),
           shortest_strings AS
           (SELECT relations_to_check.SentenceID, relations_to_check.HeadPos,
                   relations_to_check.DependentPos,
                   relations_to_check.FirstPos,
                   relations_to_check.LastPos, relations_to_check.Relation,
                   MAX(strings.Start) AS Start,
                   MIN(strings.Stop) AS Stop
            FROM relations_to_check
                 LEFT JOIN gnt.strings
                 ON relations_to_check.SentenceID = strings.SentenceID
                    AND FirstPos >= Start
                    AND FirstPos <= Stop
                    AND LastPos >= Start
                    AND LastPos <= Stop
            GROUP BY relations_to_check.SentenceID, relations_to_check.HeadPos,
                     relations_to_check.DependentPos,
                     relations_to_check.FirstPos,
                     relations_to_check.LastPos,
                     relations_to_check.Relation),
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
      FROM shortest_strings
           LEFT JOIN gnt.strings
           ON shortest_strings.SentenceID = strings.SentenceID
              AND shortest_strings.Start = strings.Start
              AND shortest_strings.Stop = strings.Stop
           LEFT JOIN book_chapter_verse
           ON shortest_strings.SentenceID = book_chapter_verse.SentenceID
      ORDER BY book_chapter_verse.Book, book_chapter_verse.Chapter,
               book_chapter_verse.Verse, shortest_strings.HeadPos
      LIMIT 50;" | mysql -u root -p$MYSQL_PASSWORD 2>/dev/null | while IFS=$'\t' read citation string sentence_id head_pos dependent_pos relation
do
  if [ "$citation" != "Citation" ]
  then
    citation_string=$citation
    if [ "$citation" == "NULL" ]
    then
      citation_string=$sentence_id
    fi
    colored_string=$(echo "$string" | sed ''/H/s//`printf "\e[1;35m"`/'' | sed ''/h/s//`printf "\e[0m"`/'' | sed ''/D/s//`printf "\e[1;36m"`/'' | sed ''/d/s//`printf "\e[0m"`/'')
    if [ "$colored_string" == "NULL" ]
    then
      colored_string="$head_pos $dependent_pos"
    fi
    echo "$citation_string ($relation): $colored_string"
    echo ""
  fi
done
