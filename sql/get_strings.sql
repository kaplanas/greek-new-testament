CREATE OR REPLACE VIEW study_strings AS
WITH expanded_nominal_types AS
     (SELECT unique_nominal_types.NominalType AS WordNominalType,
             all_nominal_types.NominalType
      FROM (SELECT DISTINCT NominalType
            FROM words
            WHERE NominalType IS NOT NULL) unique_nominal_types
           JOIN (SELECT DISTINCT NominalType
                 FROM words
                 WHERE NominalType NOT LIKE '%,%') all_nominal_types
           ON REGEXP_LIKE(unique_nominal_types.NominalType,
                          CONCAT('(^|, )', all_nominal_types.NominalType, '($|,)'))),
     expanded_noun_class_types AS
     (SELECT unique_noun_class_types.NounClassType AS WordNounClassType,
             all_noun_class_types.NounClassType
      FROM (SELECT DISTINCT NounClassType
            FROM words
            WHERE NounClassType IS NOT NULL) unique_noun_class_types
           JOIN (SELECT DISTINCT NounClassType
                 FROM words
                 WHERE NounClassType NOT LIKE '%;%') all_noun_class_types
           ON REGEXP_LIKE(unique_noun_class_types.NounClassType,
                          CONCAT('(^|; )', all_noun_class_types.NounClassType, '($|;)'))),
     word_status AS
     (SELECT words.SentenceID, words.SentencePosition, POS,
             CASE WHEN required_nominal_types.SentenceID IS NOT NULL
                       THEN words.NominalType
             END AS ActualNominalType,
             nominal_types.FeatureValue AS NominalTypeFeatureValue,
             nominal_types.Required AS NominalTypeRequired,
             CASE WHEN required_noun_class_types.SentenceID IS NOT NULL
                       THEN words.NounClassType
             end as ActualNounClassType,
             noun_class_types.FeatureValue AS NounClassTypeFeatureValue,
             noun_class_types.Required AS NounClassTypeRequired,
             CASE WHEN required_verb_class_types.SentenceID IS NOT NULL
                       THEN words.VerbClassType
             end as ActualVerbClassType,
             verb_class_types.FeatureValue AS VerbClassTypeFeatureValue,
             verb_class_types.Required AS VerbClassTypeRequired,
             other_pos.FeatureValue AS OtherPOSFeatureValue,
             other_pos.Required AS OtherPOSRequired,
             words.Degree, adjectives.FeatureValue AS AdjectiveFeatureValue,
             adjectives.Required AS AdjectiveRequired,
             tense_mood.FeatureValue AS TenseMoodFeatureValue,
             tense_mood.Required AS TenseMoodRequired,
             voice.FeatureValue AS VoiceFeatureValue,
             voice.Required AS VoiceRequired
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
           LEFT JOIN (SELECT DISTINCT SentenceID, SentencePosition
                      FROM required_types
                      WHERE TypeName = 'NounClassType') required_noun_class_types
           ON words.SentenceID = required_noun_class_types.SentenceID
              AND words.SentencePosition = required_noun_class_types.SentencePosition
           LEFT JOIN expanded_noun_class_types
           ON words.NounClassType = expanded_noun_class_types.WordNounClassType
           LEFT JOIN (SELECT FeatureValue, Required
                      FROM students_words
                      WHERE StudentID = 1
                            AND Feature = 'NounClassType') noun_class_types
           ON expanded_noun_class_types.NounClassType = noun_class_types.FeatureValue
           LEFT JOIN (SELECT DISTINCT SentenceID, SentencePosition
                      FROM required_types
                      WHERE TypeName = 'VerbClassType') required_verb_class_types
           ON words.SentenceID = required_verb_class_types.SentenceID
              AND words.SentencePosition = required_verb_class_types.SentencePosition
           LEFT JOIN (SELECT FeatureValue, Required
                      FROM students_words
                      WHERE StudentID = 1
                            AND Feature = 'VerbClassType') verb_class_types
           ON words.VerbClassType = verb_class_types.FeatureValue
           LEFT JOIN (SELECT FeatureValue, Required
                      FROM students_words
                      WHERE StudentID = 1
                            AND Feature = 'POS') other_pos
           ON words.POS = other_pos.FeatureValue
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
           ON words.Voice = voice.FeatureValue),
     forbidden_words AS
     (SELECT DISTINCT SentenceID, SentencePosition
      FROM word_status
      WHERE (ActualNominalType IS NOT NULL
             AND NominalTypeFeatureValue IS NULL)
            OR ((ActualNounClassType IS NOT NULL
                 AND NounClassTypeFeatureValue IS NULL))
            OR ((ActualVerbClassType IS NOT NULL
                 AND VerbClassTypeFeatureValue IS NULL))
            OR OtherPOSFeatureValue IS NULL
            OR (OtherPOSFeatureValue = 'adj'
                AND Degree IS NOT NULL
                AND AdjectiveFeatureValue IS NULL)
            OR (POS = 'verb' AND
                (TenseMoodFeatureValue IS NULL
                 OR VoiceFeatureValue IS NULL))),
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
            OR NounClassTypeRequired
            OR VerbClassTypeRequired
            OR OtherPOSRequired
            OR TenseMoodRequired
            OR VoiceRequired),
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
     longest_strings AS
     (SELECT filtered_strings.SentenceID, filtered_strings.Start,
             filtered_strings.Stop
      FROM filtered_strings
           LEFT JOIN filtered_strings super_strings
           ON filtered_strings.SentenceID = super_strings.SentenceID
              AND filtered_strings.Start >= super_strings.Start
              AND filtered_strings.Stop <= super_strings.Stop
              AND NOT (filtered_strings.Start = super_strings.Start
                       AND filtered_strings.Stop = super_strings.Stop)
      WHERE super_strings.SentenceID IS NULL),
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
           JOIN longest_strings
           ON filtered_strings.SentenceID = longest_strings.SentenceID
              AND filtered_strings.Start = longest_strings.Start
              AND filtered_strings.Stop = longest_strings.Stop) final_strings
     JOIN book_chapter_verse
     ON final_strings.SentenceID = book_chapter_verse.SentenceID
ORDER BY book_chapter_verse.Book, book_chapter_verse.FirstChapter,
         book_chapter_verse.FirstVerse, book_chapter_verse.FirstPosition;
