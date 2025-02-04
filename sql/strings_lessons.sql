CREATE OR REPLACE VIEW strings_lessons AS
WITH strings_words_relations AS
     (SELECT s.Start, s.Stop, w.*, r.Relation
      FROM gnt.strings s
           JOIN gnt.words w
           ON s.SentenceID = w.SentenceID
              AND s.Start <= w.SentencePosition
              AND s.Stop >= w.SentencePosition
           LEFT JOIN gnt.relations r
           ON s.SentenceID = r.SentenceID
              AND w.SentencePosition = r.DependentPos
                  AND s.Start <= r.HeadPos
                  AND s.Stop >= r.HeadPos)
SELECT DISTINCT swr.SentenceID, swr.Start, swr.Stop, l.LessonID
FROM strings_words_relations swr
     JOIN gnt.lessons l
     ON l.LessonGroup = 'Case'
        AND swr.NCase = LOWER(l.LessonName)
UNION ALL
SELECT DISTINCT swr.SentenceID, swr.Start, swr.Stop, l.LessonID
FROM strings_words_relations swr
     JOIN gnt.lessons l
     ON l.LessonGroup = 'Noun class'
        AND swr.POS IN ('noun', 'reflexive pronoun', 'demonstrative pronoun',
                        'demonstrative pronoun with kai',
                        'interrogative pronoun', 'indefinite pronoun',
                        'relative pronoun')
        AND ((l.LessonName = 'Second declension'
              AND swr.NounClassType IN ('first/second declension',
                                        'first declension with hs',
                                        'first/second declension; third declension, consonant stem'))
             OR (l.LessonName = 'First declension'
                 AND swr.NounClassType IN ('first/second declension',
                                           'first declension with hs',
                                           'first/second declension; third declension, consonant stem'))
             OR (l.LessonName = 'Third declension'
                 AND swr.NounClassType IN ('third declension, vowel stem',
                                           'third declension, consonant stem',
                                           'first/second declension; third declension, consonant stem'))
             OR (l.LessonName = 'Ἰησοῦς' AND swr.NounClassType = 'Ihsous')
             OR swr.NounClassType = LOWER(l.LessonName))
UNION ALL
SELECT DISTINCT swr.SentenceID, swr.Start, swr.Stop, l.LessonID
FROM strings_words_relations swr
     JOIN gnt.lessons l
     ON l.LessonGroup = 'Adjective class'
        AND swr.POS = 'adj'
        AND ((l.LessonName = 'First and second declension'
              AND swr.NounClassType = 'first/second declension')
             OR (l.LessonName = 'Third declension'
                 AND swr.NounClassType IN ('third declension, vowel stem',
                                           'third declension, consonant stem'))
             OR swr.NounClassType = LOWER(l.LessonName))
UNION ALL
SELECT DISTINCT swr.SentenceID, swr.Start, swr.Stop, l.LessonID
FROM strings_words_relations swr
     JOIN gnt.lessons l
     ON l.LessonGroup = 'Adjective forms'
        AND CONCAT(swr.Degree, 's') = LOWER(l.LessonName)
UNION ALL
SELECT DISTINCT swr.SentenceID, swr.Start, swr.Stop, l.LessonID
FROM strings_words_relations swr
     JOIN gnt.lessons l
     ON l.LessonGroup = 'Verb class'
        AND ((l.LessonName = 'Εἰμί' AND swr.VerbClassType = 'eimi')
             OR (l.LessonName = 'Contract, έω'
                 AND swr.VerbClassType = 'contract, ew')
             OR (l.LessonName = 'Contract, άω'
                 AND swr.VerbClassType = 'contract, aw')
             OR (l.LessonName = 'Contract, όω'
                 AND swr.VerbClassType = 'contract, ow')
             OR (l.LessonName = 'Μί' AND swr.VerbClassType = 'mi')
             OR (l.LessonName = 'Οἶδα' AND swr.VerbClassType = 'oida')
             OR swr.VerbClassType = LOWER(l.LessonName))
UNION ALL
SELECT DISTINCT swr.SentenceID, swr.Start, swr.Stop, l.LessonID
FROM strings_words_relations swr
     JOIN gnt.lessons l
     ON l.LessonGroup = 'Tense and mood'
        AND CONCAT(swr.Tense, ' ', swr.Mood) = LOWER(l.LessonName)
UNION ALL
SELECT DISTINCT swr.SentenceID, swr.Start, swr.Stop, l.LessonID
FROM strings_words_relations swr
     JOIN gnt.lessons l
     ON l.LessonGroup = 'Voice'
        AND swr.Voice = LOWER(l.LessonName)
UNION ALL
SELECT DISTINCT swr.SentenceID, swr.Start, swr.Stop, l.LessonID
FROM strings_words_relations swr
     JOIN gnt.lessons l
     ON l.LessonGroup = 'Pronouns'
        AND ((l.LessonName = 'Personal pronouns'
              AND swr.POS = 'personal pronoun with kai')
             OR (l.LessonName = 'Reflexive pronouns'
                 AND swr.POS = 'reflexive adverb')
             OR (l.LessonName = 'Demonstrative pronouns'
                 AND swr.POS = 'demonstrative pronoun with kai')
             OR (l.LessonName = 'Interrogative pronouns'
                 AND swr.POS = 'interrogative adverb')
             OR (l.LessonName = 'Indefinite pronouns'
                 AND swr.POS = 'indefinite adverb')
             OR (l.LessonName = 'Relative pronouns'
                 AND (swr.POS = 'relative adverb'
                      OR swr.Relation IN ('subject, attraction',
                                          'subject of infinitive, attraction',
                                          'direct object, attraction',
                                          'indirect object, attraction',
                                          'other, attraction',
                                          'resumptive pronoun')))
             OR CONCAT(swr.POS, 's') = LOWER(l.LessonName))
UNION ALL
SELECT DISTINCT swr.SentenceID, swr.Start, swr.Stop, l.LessonID
FROM strings_words_relations swr
     JOIN gnt.lessons l
     ON l.LessonGroup = 'Other parts of speech'
        AND ((l.LessonName = 'Definite article' AND swr.POS = 'det')
             OR (l.LessonName = 'Second-position clitics'
                 AND swr.Relation = 'second-position clitic')
             OR (l.LessonName = 'Prepositions' AND swr.POS = 'prep')
             OR (l.LessonName = 'Coordinating conjunctions'
                 AND (swr.POS IN ('personal pronoun with kai',
                                  'demonstrative pronoun with kai',
                                  'adverb with kai')
                      OR swr.Relation = 'conjunct'))
             OR (l.LessonName = 'Subordinating conjunctions'
                 AND swr.Relation IN ('conjunct, main',
                                      'conjunct, subordinate',
                                      'conjunct, ὡς, clause',
                                      'conjunct, ὡς, non-clause',
                                      'conjunct, ὡς, other'))
             OR (l.LessonName = 'Adverbs'
                 AND swr.POS IN ('adv', 'adverb with kai', 'indefinite adverb',
                                 'interrogative adverb', 'reflexive adverb'))
             OR (l.LessonName = 'Numbers'
                 AND (swr.POS = 'num' OR swr.Relation = 'number'))
             OR (l.LessonName = 'Particles' AND swr.POS IN ('ptcl', 'intj'))
             OR swr.POS = LOWER(l.LessonName))
UNION ALL
SELECT DISTINCT swr.SentenceID, swr.Start, swr.Stop, l.LessonID
FROM strings_words_relations swr
     JOIN gnt.lessons l
     ON l.LessonGroup = 'Syntactic structures'
        AND ((l.LessonName = 'Comparison' AND swr.Relation = 'conjunct, ἤ')
             OR (l.LessonName = 'Indirect discourse'
                 AND swr.Relation IN ('sentential complement', 'conjunct, ὅτι',
                                      'clause argument of verb',
                                      'subject of implicit speech'))
             OR (l.LessonName = 'Topics' AND swr.Relation = 'topic'));

CREATE OR REPLACE VIEW strings_properties AS
WITH strings_words_relations AS
     (SELECT s.Start, s.Stop, w.*, r.Relation
      FROM gnt.strings s
           JOIN gnt.words w
           ON s.SentenceID = w.SentenceID
              AND s.Start <= w.SentencePosition
              AND s.Stop >= w.SentencePosition
           LEFT JOIN gnt.relations r
           ON s.SentenceID = r.SentenceID
              AND w.SentencePosition = r.DependentPos
              AND s.Start <= r.FirstPos
              AND s.Stop >= r.LastPos
              AND r.Relation NOT IN ('appositive', 'conjunct, chain',
                                     'determiner', 'entitled', 'gap', 'name',
                                     'negation, double', 'parenthetical',
                                     'particle', 'subject of small clause',
                                     'title'))
SELECT DISTINCT SentenceID, Start, Stop, 'NounClassType' AS Property,
       NounClassType AS Value
FROM strings_words_relations
WHERE POS = 'noun'
UNION ALL
SELECT DISTINCT SentenceID, Start, Stop, 'AdjectiveClassType' AS Property,
       NounClassType AS Value
FROM strings_words_relations
WHERE POS = 'adj'
UNION ALL
SELECT DISTINCT SentenceID, Start, Stop, 'Degree' AS Property,
       Degree AS Value
FROM strings_words_relations
WHERE Degree IS NOT NULL
UNION ALL
SELECT DISTINCT SentenceID, Start, Stop, 'GenitiveCase' AS Property,
       CASE WHEN Relation LIKE '%genitive%'
                 THEN Relation
            WHEN Relation = 'direct object'
                 THEN 'direct object, genitive'
       END AS Value
FROM strings_words_relations
WHERE Relation LIKE '%genitive%'
      OR (Relation = 'direct object' AND CaseType = 'genitive')
UNION ALL
SELECT DISTINCT SentenceID, Start, Stop, 'DativeCase' AS Property,
       CASE WHEN Relation LIKE '%dative%' OR Relation = 'indirect object'
                 THEN Relation
            WHEN Relation = 'direct object'
                 THEN 'direct object, dative'
       END AS Value
FROM strings_words_relations
WHERE Relation LIKE '%dative%'
      OR Relation = 'indirect object'
      OR (Relation = 'direct object' AND CaseType = 'dative')
UNION ALL
SELECT DISTINCT SentenceID, Start, Stop, 'AccusativeCase' AS Property,
       CASE WHEN Relation LIKE '%accusative%'
                 THEN Relation
            WHEN Relation = 'direct object'
                 THEN 'direct object, accusative'
       END AS Value
FROM strings_words_relations
WHERE Relation LIKE '%accusative%'
      OR (Relation = 'direct object' AND CaseType = 'accusative')
UNION ALL
SELECT DISTINCT swr.SentenceID, swr.Start, swr.Stop, 'NominalHead' AS Property,
       swr.NominalType AS Value
FROM strings_words_relations swr
     LEFT JOIN relations r2
     ON swr.SentenceID = r2.SentenceID
        AND swr.SentencePosition = r2.HeadPos
        AND (r2.Relation LIKE 'negation%nominal'
             OR r2.Relation LIKE 'modifier of nominal%'
             OR r2.Relation = 'appositive')
     LEFT JOIN relations r3
     ON swr.SentenceID = r3.SentenceID
        AND swr.SentencePosition = r3.DependentPos
        AND (r3.Relation LIKE 'subject%'
             OR r3.Relation LIKE 'genitive%'
             OR r3.Relation LIKE 'direct object%'
             OR r3.Relation = 'argument of adjective, nominal'
             OR r3.Relation LIKE 'accusative%'
             OR r3.Relation LIKE 'indirect object%'
             OR r3.Relation LIKE 'dative%'
             OR r3.Relation = 'interjection, vocative'
             OR r3.Relation = 'object of preposition'
             OR r3.Relation = 'resumptive pronoun'
             OR r3.Relation = 'topic'
             OR r3.Relation = 'appositive')
     LEFT JOIN relations r4
     ON swr.SentenceID = r4.SentenceID
        AND swr.SentencePosition = r4.HeadPos
        AND (swr.Start > r4.FirstPos
             OR swr.Stop < r4.LastPos)
        AND r4.Relation = 'conjunct, main'
     LEFT JOIN relations r5
     ON swr.SentenceID = r5.SentenceID
        AND swr.SentencePosition = r5.DependentPos
        AND swr.Start <= r5.FirstPos
        AND swr.Stop >= r5.LastPos
        AND r5.Relation = 'determiner'
     LEFT JOIN relations r6
     ON swr.SentenceID = r6.SentenceID
        AND swr.SentencePosition = r6.HeadPos
        AND r6.Relation = 'subject of small clause'
WHERE (r2.SentenceID IS NOT NULL OR r3.SentenceID IS NOT NULL)
      AND r4.SentenceID IS NULL
      AND (swr.NominalType LIKE '%adjective%'
           OR swr.SentenceID IS NOT NULL
           OR r5.SentenceID IS NOT NULL)
      AND r6.SentenceID IS NULL
UNION ALL
SELECT DISTINCT SentenceID, Start, Stop, 'VerbClassType' AS Property,
       VerbClassType AS Value
FROM strings_words_relations
WHERE VerbClassType IS NOT NULL
UNION ALL
SELECT DISTINCT SentenceID, Start, Stop, 'TenseMood' AS Property,
       CONCAT(Tense, '-', Mood) AS Value
FROM strings_words_relations
WHERE Tense IS NOT NULL OR Mood IS NOT NULL
UNION ALL
SELECT DISTINCT SentenceID, Start, Stop, 'Voice' AS Property, Voice AS Value
FROM strings_words_relations
WHERE Voice IS NOT NULL
UNION ALL
SELECT DISTINCT SentenceID, Start, Stop, 'VerbModifier' AS Property,
       REGEXP_REPLACE(Relation, 'modifier of verb(less predicate)?, ',
                      '') AS Value
FROM strings_words_relations
WHERE Relation LIKE 'modifier of verb%'
UNION ALL
SELECT DISTINCT SentenceID, Start, Stop, 'POS' AS Property, POS AS Value
FROM strings_words_relations
UNION ALL
SELECT DISTINCT SentenceID, Start, Stop, 'Subject' AS Property,
       Relation AS Value
FROM strings_words_relations
WHERE Relation LIKE 'subject%'
UNION ALL
SELECT DISTINCT SentenceID, Start, Stop, 'Negation' AS Property,
       Relation AS Value
FROM strings_words_relations
WHERE Relation LIKE 'negation%'
UNION ALL
SELECT DISTINCT swr.SentenceID, swr.Start, swr.Stop,
       'NominalModifier' AS Property,
       CASE WHEN swr.Relation = 'modifier of nominal, nominal'
                 AND r4.SentenceID IS NULL
                 THEN swr.NominalType
            WHEN swr.Relation = 'modifier of nominal, adverb'
                 THEN 'adverb'
            WHEN swr.Relation = 'modifier of nominal, infinitive'
                 THEN 'infinitive'
            WHEN swr.Relation = 'modifier of nominal, PP'
                 THEN 'prepositional phrase'
            WHEN swr.Relation = 'infinitive argument of noun'
                 THEN 'infinitive'
       END AS Value
FROM strings_words_relations swr
     LEFT JOIN relations r4
     ON swr.SentenceID = r4.SentenceID
        AND swr.SentencePosition = r4.HeadPos
        AND (swr.Start > r4.FirstPos OR swr.Stop < r4.LastPos)
        AND r4.Relation = 'conjunct, main'
WHERE swr.Relation IN ('modifier of nominal, adverb',
                       'modifier of nominal, infinitive',
                       'modifier of nominal, PP',
                       'infinitive argument of noun')
      OR (swr.Relation = 'modifier of nominal, nominal'
          AND r4.SentenceID IS NULL)
UNION ALL
SELECT DISTINCT SentenceID, Start, Stop, 'Conjunction' AS Property,
       Relation AS Value
FROM strings_words_relations
WHERE Relation LIKE 'conjunct%'
UNION ALL
SELECT DISTINCT SentenceID, Start, Stop, 'Relation' AS Property,
       Relation AS Value
FROM strings_words_relations;