echo "WITH word_positions AS
           (SELECT SentenceID, Book, Chapter, Verse, VersePosition,
                   SentencePosition,
                   CASE WHEN Book = 'Matt' THEN 1
                        WHEN Book = 'Mark' THEN 2
                        WHEN Book = 'Luke' THEN 3
                        WHEN Book = 'John' THEN 4
                        WHEN Book = 'Acts' THEN 5
                        WHEN Book = 'Rom' THEN 6
                        WHEN Book = '1Cor' THEN 7
                        WHEN Book = '2Cor' THEN 8
                        WHEN Book = 'Gal' THEN 9
                        WHEN Book = 'Eph' THEN 10
                        WHEN Book = 'Phil' THEN 11
                        WHEN Book = 'Col' THEN 12
                        WHEN Book = '1Thess' THEN 13
                        WHEN Book = '2Thess' THEN 14
                        WHEN Book = '1Tim' THEN 15
                        WHEN Book = '2Tim' THEN 16
                        WHEN Book = 'Titus' THEN 17
                        WHEN Book = 'Phlm' THEN 18
                        WHEN Book = 'Heb' THEN 19
                        WHEN Book = 'Jas' THEN 20
                        WHEN Book = '1Pet' THEN 21
                        WHEN Book = '2Pet' THEN 22
                        WHEN Book = '1John' THEN 23
                        WHEN Book = '2John' THEN 24
                        WHEN Book = '3John' THEN 25
                        WHEN Book = 'Jude' THEN 26
                        WHEN Book = 'Rev' THEN 27
                   END AS BookOrder,
                   ROW_NUMBER()
                   OVER (PARTITION BY SentenceID
                         ORDER BY Verse, VersePosition) ROW_NUM_1,
                   ROW_NUMBER()
                   OVER (PARTITION BY SentenceID
                         ORDER BY Verse DESC, VersePosition DESC) ROW_NUM_2
            FROM gnt.words),
           sentence_ids AS
           (SELECT wp1.SentenceID, wp1.Book, wp1.BookOrder, wp1.Chapter,
                   wp1.Verse AS FirstVerse,
                   wp1.VersePosition AS FirstVersePosition,
                   wp2.Verse AS LastVerse,
                   wp2.VersePosition AS LastVersePosition
            FROM word_positions wp1
                 JOIN word_positions wp2
                 ON wp1.SentenceID = wp2.SentenceID
            WHERE wp1.ROW_NUM_1 = 1
                  AND wp2.ROW_NUM_2 = 1),
           overlaps AS
           (SELECT CONCAT(s1.SentenceID, ' | ', s2.SentenceID) AS WonkyNote,
                   s1.BookOrder, s1.Chapter, s1.FirstVerse AS Verse,
                   s1.FirstVersePosition AS VersePosition
            FROM sentence_ids s1
                 JOIN sentence_ids s2
                 ON s1.SentenceID <> s2.SentenceID
                    AND s1.Book = s2.Book
                    AND s1.Chapter = s2.Chapter
                    AND s1.FirstVerse <= s2.FirstVerse
                    AND (s1.FirstVerse < s2.FirstVerse
                         OR s1.FirstVersePosition <= s2.FirstVersePosition)
                    AND s1.LastVerse >= s2.LastVerse
                    AND (s1.LastVerse > s2.LastVerse
                         OR s1.LastVersePosition >= s2.LastVersePosition)),
           gaps AS
           (SELECT wp.SentenceID AS WonkyNote, wp.BookOrder, wp.Chapter,
                   wp.Verse, wp.VersePosition
            FROM word_positions wp
                 LEFT JOIN gnt.strings s
                 ON wp.SentenceID = s.SentenceID
                    AND wp.SentencePosition >= s.Start
                    AND wp.SentencePosition <= s.Stop
            WHERE wp.SentenceID NOT IN
                  ('Mark 2:7.5 - Mark 2:7.5',
                   'Mark 14:41.13 - Mark 14:41.13',
                   'Mark 16:6.13 - Mark 16:6.13',
                   'Mark 16:8.52 - Mark 16:8.52',
                   'Luke 7:26.5 - Luke 7:26.5',
                   'Luke 10:3.1 - Luke 10:3.1',
                   'Acts 15:29.15 - Acts 15:29.15',
                   'Rom 3:9.3 - Rom 3:9.3',
                   'Rom 3:27.5 - Rom 3:27.5',
                   'Rom 11:20.1 - Rom 11:20.1',
                   '1Cor 7:36.22 - 1Cor 7:36.22',
                   '1Cor 16:13.1 - 1Cor 16:13.1',
                   '1Cor 16:13.6 - 1Cor 16:13.6',
                   '1Cor 16:13.7 - 1Cor 16:13.7',
                   '2Cor 11:22.3 - 2Cor 11:22.3',
                   '2Cor 11:22.6 - 2Cor 11:22.6',
                   '2Cor 11:22.10 - 2Cor 11:22.10',
                   '2Tim 4:5.6 - 2Tim 4:5.6',
                   'Jas 5:13.5 - Jas 5:13.5',
                   'Jas 5:13.8 - Jas 5:13.8')
            GROUP BY wp.SentenceID, wp.BookOrder, wp.Chapter, wp.Verse,
                     wp.VersePosition
            HAVING SUM(CASE WHEN s.SentenceID IS NOT NULL THEN 1 END) <= 1)
      SELECT WonkyNote
      FROM (SELECT * FROM overlaps
            UNION ALL
            SELECT * FROM gaps) og
      GROUP BY WonkyNote
      ORDER BY MIN(BookOrder), MIN(Chapter), MIN(Verse), MIN(VersePosition)
      LIMIT 10;" | mysql -u root -p$MYSQL_PASSWORD 2>/dev/null | while IFS=$'\t' read wonky_note
do
  if [ "$wonky_note" != "WonkyNote" ]
  then
    echo "$wonky_note"
    echo ""
  fi
done
