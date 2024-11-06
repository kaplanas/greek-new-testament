CREATE OR REPLACE VIEW required_types AS
WITH nominal_types_dep AS
     (SELECT 'NominalType' AS TypeName, 'dep' AS HeadOrDep, SentenceID,
             DependentPos AS SentencePosition, HeadPos AS OtherPosition,
             Relation, 1 AS CheckOrder
      FROM gnt.checked_relation_tokens
      WHERE Relation LIKE 'subject%'
            OR Relation = 'predicate, nominal'
            OR Relation LIKE 'genitive%'
            OR Relation LIKE 'direct object%'
            OR Relation LIKE 'argument of adjective%'
            OR Relation LIKE 'accusative%'
            OR Relation LIKE 'indirect object%'
            OR Relation LIKE 'dative%'
            OR Relation = 'interjection, vocative'
            OR Relation = 'modifier of nominal, nominal'
            OR Relation LIKE 'modifier of verb%nominal'
            OR Relation = 'object of preposition'
            OR Relation LIKE 'subject of infinitive%'
            OR Relation = 'resumptive pronoun'),
     nominal_types_head AS
     (SELECT 'NominalType' AS TypeName, 'head' AS HeadOrDep, SentenceID,
             HeadPos AS SentencePosition, DependentPos AS OtherPosition,
             Relation, 1 AS CheckOrder
      FROM gnt.checked_relation_tokens
      WHERE Relation LIKE 'argument of adjective%'
            OR Relation LIKE 'negation%nominal'
            OR Relation LIKE 'determiner%'
            OR Relation LIKE 'modifier of nominal%'),
     noun_class_types_dep AS
     (SELECT 'NounClassType' AS TypeName, 'dep' AS HeadOrDep,
             checked_relation_tokens.SentenceID,
             checked_relation_tokens.DependentPos AS SentencePosition,
             checked_relation_tokens.HeadPos AS OtherPosition,
             checked_relation_tokens.Relation, 2 AS CheckOrder
      FROM gnt.checked_relation_tokens
           JOIN gnt.words dep
           ON checked_relation_tokens.SentenceID = dep.SentenceID
              AND checked_relation_tokens.DependentPos = dep.SentencePosition
      WHERE (dep.POS LIKE '%noun%'
             AND dep.POS NOT LIKE 'personal pronoun%')
            OR (dep.POS = 'adj')),
     noun_class_types_head AS
     (SELECT 'NounClassType' AS TypeName, 'head' AS HeadOrDep,
             checked_relation_tokens.SentenceID,
             checked_relation_tokens.HeadPos AS SentencePosition,
             checked_relation_tokens.DependentPos AS OtherPosition,
             checked_relation_tokens.Relation, 2 AS CheckOrder
      FROM gnt.checked_relation_tokens
           JOIN gnt.words head
           ON checked_relation_tokens.SentenceID = head.SentenceID
              AND checked_relation_tokens.HeadPos = head.SentencePosition
      WHERE (head.POS LIKE '%noun%'
             AND head.POS NOT LIKE 'personal pronoun%')
            OR (head.POS = 'adj')),
     case_types_dep AS
     (SELECT 'CaseType' AS TypeName, 'dep' AS HeadOrDep, SentenceID,
             DependentPos AS SentencePosition, HeadPos AS OtherPosition,
             Relation, 3 AS CheckOrder
      FROM gnt.checked_relation_tokens
      WHERE Relation LIKE 'subject of infinitive%'
            OR Relation LIKE 'genitive%'
            OR Relation LIKE 'direct object%'
            OR Relation LIKE 'accusative%'
            OR Relation LIKE 'indirect object%'
            OR Relation LIKE 'dative%'
            OR Relation = 'interjection, vocative'
            OR Relation = 'predicate, nominal'
            OR Relation = 'argument of adjective, nominal'
            OR Relation = 'object of preposition'
            OR Relation = 'resumptive pronoun'
            OR Relation = 'modifier of verb, participle'),
     case_types_head AS
     (SELECT 'CaseType' AS TypeName, 'head' AS HeadOrDep, SentenceID,
             HeadPos AS SentencePosition, DependentPos AS OtherPosition,
             Relation, 3 AS CheckOrder
      FROM gnt.checked_relation_tokens
      WHERE Relation LIKE 'negation%nominal'
            OR Relation = 'infinitive argument of noun'),
     verb_class_types_dep AS
     (SELECT 'VerbClassType' AS TypeName, 'dep' AS HeadOrDep,
             checked_relation_tokens.SentenceID,
             checked_relation_tokens.DependentPos AS SentencePosition,
             checked_relation_tokens.HeadPos AS OtherPosition,
             checked_relation_tokens.Relation, 4 AS CheckOrder
      FROM gnt.checked_relation_tokens
           JOIN gnt.words dep
           ON checked_relation_tokens.SentenceID = dep.SentenceID
              AND checked_relation_tokens.DependentPos = dep.SentencePosition
      WHERE dep.POS = 'verb'),
     verb_class_types_head AS
     (SELECT 'VerbClassType' AS TypeName, 'head' AS HeadOrDep,
             checked_relation_tokens.SentenceID,
             checked_relation_tokens.HeadPos AS SentencePosition,
             checked_relation_tokens.DependentPos AS OtherPosition,
             checked_relation_tokens.Relation, 4 AS CheckOrder
      FROM gnt.checked_relation_tokens
           JOIN gnt.words head
           ON checked_relation_tokens.SentenceID = head.SentenceID
              AND checked_relation_tokens.HeadPos = head.SentencePosition
      WHERE head.POS = 'verb')
SELECT TypeName, HeadOrDep, SentenceID, SentencePosition, OtherPosition,
       Relation, CheckOrder
FROM (SELECT * FROM nominal_types_dep
      UNION
      SELECT * FROM nominal_types_head
      UNION
      SELECT * FROM noun_class_types_dep
      UNION
      SELECT * FROM noun_class_types_head
      UNION
      SELECT * FROM case_types_dep
      UNION
      SELECT * FROM case_types_head
      UNION
      SELECT * FROM verb_class_types_dep
      UNION
      SELECT * FROM verb_class_types_head) all_types;
