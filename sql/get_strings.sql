CREATE OR REPLACE VIEW study_strings AS
WITH forbidden_words AS
     (SELECT SentenceID, SentencePosition
      FROM words
           LEFT JOIN (SELECT FeatureValue
                      FROM students_words
                      WHERE StudentID = 1
                            AND Feature = 'POS') other_pos
           ON words.POS = other_pos.FeatureValue
           LEFT JOIN (SELECT FeatureValue
                      FROM students_words
                      WHERE StudentID = 1
                            AND Feature = 'NounClass') nouns
           ON words.NounClass = nouns.FeatureValue
           LEFT JOIN (SELECT FeatureValue
                      FROM students_words
                      WHERE StudentID = 1
                            AND Feature = 'TenseMood') tense_mood
           ON CONCAT(words.Tense, '-', words.Mood) = tense_mood.FeatureValue
           LEFT JOIN (SELECT FeatureValue
                      FROM students_words
                      WHERE StudentID = 1
                            AND Feature = 'Voice') voice
           ON words.Voice = voice.FeatureValue
           LEFT JOIN (SELECT FeatureValue
                      FROM students_words
                      WHERE StudentID = 1
                            AND Feature = 'VerbClass') verb_class
           ON words.VerbClass = verb_class.FeatureValue
      WHERE other_pos.FeatureValue IS NULL
            AND (words.POS <> 'noun' OR nouns.FeatureValue IS NULL)
            AND (words.POS <> 'verb' OR
                 tense_mood.FeatureValue IS NULL
                 OR voice.FeatureValue IS NULL
                 OR verb_class.FeatureValue IS NULL)),
     strings_filtered_by_words AS
     (SELECT strings.SentenceID, Start, Stop, Citation, String
      FROM strings
           LEFT JOIN forbidden_words
           ON strings.SentenceID = forbidden_words.SentenceID
              AND SentencePosition >= Start
              AND SentencePosition <= Stop
      WHERE forbidden_words.SentenceID IS NULL
            AND Stop > Start),
     forbidden_relations AS
     (SELECT SentenceID, FirstPos, LastPos
      FROM relations
           LEFT JOIN students_relations
           ON StudentID = 1
              AND relations.Relation = students_relations.Relation
      WHERE StudentID IS NULL),
     allowed_strings AS
     (SELECT strings_filtered_by_words.SentenceID, Start, Stop, Citation, String
      FROM strings_filtered_by_words
           LEFT JOIN forbidden_relations
           ON strings_filtered_by_words.SentenceID = forbidden_relations.SentenceID
              AND FirstPos >= Start
              AND FirstPos <= Stop
              AND LastPos >= Start
              AND LastPos <= Stop
     WHERE forbidden_relations.SentenceID IS NULL),
     required_relations AS
     (SELECT SentenceID, FirstPos, LastPos
      FROM relations
           JOIN students_relations
           ON StudentID = 1
              AND relations.Relation = students_relations.Relation
              AND Required),
     filtered_strings AS
     (SELECT allowed_strings.SentenceID, Start, Stop, Citation, String
      FROM allowed_strings
           LEFT JOIN required_relations
           ON allowed_strings.SentenceID = required_relations.SentenceID
              AND FirstPos >= Start
              AND FirstPos <= Stop
              AND LastPos >= Start
              AND LastPos <= Stop
      WHERE required_relations.SentenceID IS NOT NULL
            OR (SELECT COUNT(*) FROM required_relations) = 0),
     longest_strings_left AS
     (SELECT SentenceID, Start, MAX(Stop) AS LastStop
      FROM filtered_strings
      GROUP BY SentenceID, Start),
     longest_strings_right AS
     (SELECT SentenceID, MIN(Start) AS FirstStart, Stop
      FROM filtered_strings
      GROUP BY SentenceID, Stop),
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
             END AS Book, MIN(Chapter) AS FirstChapter,
             MIN(Verse) AS FirstVerse, MIN(VersePosition) AS FirstPosition
      FROM words
      GROUP BY SentenceID)
SELECT Citation, String
FROM filtered_strings
     JOIN longest_strings_left
     ON filtered_strings.SentenceID = longest_strings_left.SentenceID
        AND filtered_strings.Start = longest_strings_left.Start
        AND filtered_strings.Stop = longest_strings_left.LastStop
     JOIN longest_strings_right
     ON filtered_strings.SentenceID = longest_strings_right.SentenceID
        AND filtered_strings.Start = longest_strings_right.FirstStart
        AND filtered_strings.Stop = longest_strings_right.Stop
     JOIN book_chapter_verse
     ON filtered_strings.SentenceID = book_chapter_verse.SentenceID
ORDER BY book_chapter_verse.Book, book_chapter_verse.FirstChapter,
         book_chapter_verse.FirstVerse, book_chapter_verse.FirstPosition;