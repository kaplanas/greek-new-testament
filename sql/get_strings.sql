CREATE OR REPLACE VIEW study_strings AS
WITH expanded_nominal_types AS
     (SELECT unique_nominal_types.NominalType AS WordNominalType, all_nominal_types.NominalType
      FROM (SELECT DISTINCT NominalType
            FROM words
            WHERE NominalType IS NOT NULL) unique_nominal_types
           JOIN (SELECT DISTINCT NominalType
                 FROM words
                 WHERE NominalType NOT LIKE '%,%') all_nominal_types
           ON REGEXP_LIKE(unique_nominal_types.NominalType,
                          CONCAT('(^|, )', all_nominal_types.NominalType, '($|,)'))),
     word_status AS
     (SELECT words.SentenceID, words.SentencePosition, POS,
             CASE WHEN required_nominal_types.SentenceID IS NOT NULL
                       THEN words.NominalType
             END AS ActualNominalType,
             nominal_types.FeatureValue AS NominalTypeFeatureValue,
             nominal_types.Required AS NominalTypeRequired,
             other_pos.FeatureValue AS OtherPOSFeatureValue,
             other_pos.Required AS OtherPOSRequired,
             nouns.FeatureValue AS NounFeatureValue,
             nouns.Required AS NounRequired, words.Degree,
             adjectives.FeatureValue AS AdjectiveFeatureValue,
             adjectives.Required AS AdjectiveRequired,
             tense_mood.FeatureValue AS TenseMoodFeatureValue,
             tense_mood.Required AS TenseMoodRequired,
             voice.FeatureValue AS VoiceFeatureValue,
             voice.Required AS VoiceRequired,
             verb_class.FeatureValue AS VerbClassFeatureValue,
             verb_class.Required AS VerbClassRequired
      FROM words
           LEFT JOIN (SELECT DISTINCT SentenceID, SentencePosition
                      FROM required_types
                      WHERE TypeName = 'NominalType') required_nominal_types
           ON words.SentenceID = required_nominal_types.SentenceID
              AND words.SentencePosition = required_nominal_types.SentencePosition
           LEFT JOIN expanded_nominal_types
           ON words.NominalType = expanded_nominal_types.WordNominalType
           LEFT JOIN (SELECT FeatureValue, Required
                      FROM students_words
                      WHERE StudentID = 1
                            AND Feature = 'NominalType') nominal_types
           ON expanded_nominal_types.NominalType = nominal_types.FeatureValue
           LEFT JOIN (SELECT FeatureValue, Required
                      FROM students_words
                      WHERE StudentID = 1
                            AND Feature = 'POS') other_pos
           ON words.POS = other_pos.FeatureValue
           LEFT JOIN (SELECT FeatureValue, Required
                      FROM students_words
                      WHERE StudentID = 1
                            AND Feature = 'NounClass') nouns
           ON words.NounClass = nouns.FeatureValue
           LEFT JOIN (SELECT FeatureValue, Required
                      FROM students_words
                      WHERE StudentID = 1
                            AND Feature = 'Degree') adjectives
           ON words.Degree = adjectives.FeatureValue
           LEFT JOIN (SELECT FeatureValue, Required
                      FROM students_words
                      WHERE StudentID = 1
                            AND Feature = 'TenseMood') tense_mood
           ON CONCAT(words.Tense, '-', words.Mood) = tense_mood.FeatureValue
           LEFT JOIN (SELECT FeatureValue, Required
                      FROM students_words
                      WHERE StudentID = 1
                            AND Feature = 'Voice') voice
           ON words.Voice = voice.FeatureValue
           LEFT JOIN (SELECT FeatureValue, Required
                      FROM students_words
                      WHERE StudentID = 1
                            AND Feature = 'VerbClass') verb_class
           ON words.VerbClass = verb_class.FeatureValue),
     forbidden_words AS
     (SELECT DISTINCT SentenceID, SentencePosition
      FROM word_status
      WHERE ((ActualNominalType IS NOT NULL
              AND NominalTypeFeatureValue IS NULL)
             OR OtherPOSFeatureValue IS NULL
             OR (OtherPOSFeatureValue IN ('noun', 'adj')
                 AND NounFeatureValue IS NULL)
             OR (OtherPOSFeatureValue = 'adj'
                 AND Degree IS NOT NULL
                 AND AdjectiveFeatureValue IS NULL))
            AND (POS <> 'verb' OR
                 TenseMoodFeatureValue IS NULL
                 OR VoiceFeatureValue IS NULL
                 OR VerbClassFeatureValue IS NULL)),
     allowed_words AS
     (SELECT words.SentenceID, words.SentencePosition
      FROM words
           LEFT JOIN forbidden_words
           ON words.SentenceID = forbidden_words.SentenceID
              AND words.SentencePosition = forbidden_words.SentencePosition
      WHERE forbidden_words.SentenceID IS NULL),
     required_words AS
     (SELECT DISTINCT SentenceID, SentencePosition
      FROM word_status
      WHERE NominalTypeRequired
            OR OtherPOSRequired
            OR NounRequired
            OR TenseMoodRequired
            OR VoiceRequired
            OR VerbClassRequired),
     strings_filtered_by_words AS
     (SELECT DISTINCT strings.SentenceID, Start, Stop, Citation, String
      FROM strings
           JOIN allowed_words
           ON strings.SentenceID = allowed_words.SentenceID
              AND allowed_words.SentencePosition >= Start
              AND allowed_words.SentencePosition <= Stop
           LEFT JOIN required_words
           ON strings.SentenceID = required_words.SentenceID
              AND required_words.SentencePosition >= Start
              AND required_words.SentencePosition <= Stop
           LEFT JOIN forbidden_words
           ON strings.SentenceID = forbidden_words.SentenceID
              AND forbidden_words.SentencePosition >= Start
              AND forbidden_words.SentencePosition <= Stop
      WHERE (required_words.SentenceID IS NOT NULL
             OR (SELECT COUNT(*) FROM required_words) = 0)
            AND forbidden_words.SentenceID IS NULL
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
FROM (SELECT DISTINCT filtered_strings.SentenceID, Citation, String
      FROM filtered_strings
           JOIN longest_strings_left
           ON filtered_strings.SentenceID = longest_strings_left.SentenceID
              AND filtered_strings.Start = longest_strings_left.Start
              AND filtered_strings.Stop = longest_strings_left.LastStop
           JOIN longest_strings_right
           ON filtered_strings.SentenceID = longest_strings_right.SentenceID
              AND filtered_strings.Start = longest_strings_right.FirstStart
              AND filtered_strings.Stop = longest_strings_right.Stop) final_strings
     JOIN book_chapter_verse
     ON final_strings.SentenceID = book_chapter_verse.SentenceID
ORDER BY book_chapter_verse.Book, book_chapter_verse.FirstChapter,
         book_chapter_verse.FirstVerse, book_chapter_verse.FirstPosition;
