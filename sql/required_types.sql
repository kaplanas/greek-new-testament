CREATE OR REPLACE VIEW required_types AS
WITH nominal_types_dep AS
     (SELECT 'NominalType' AS TypeName, 'dep' AS HeadOrDep, dep.SentenceID,
             dep.SentencePosition, head.SentencePosition AS OtherPosition,
             checked_relation_tokens.Relation, 1 AS CheckOrder
      FROM gnt.checked_relation_tokens
           JOIN gnt.words head
           ON checked_relation_tokens.SentenceID = head.SentenceID
              AND checked_relation_tokens.HeadPos = head.SentencePosition
           JOIN gnt.words dep
           ON checked_relation_tokens.SentenceID = dep.SentenceID
              AND checked_relation_tokens.DependentPos = dep.SentencePosition
      WHERE checked_relation_tokens.Relation LIKE 'subject%'
            OR checked_relation_tokens.Relation = 'predicate, nominal'
            OR checked_relation_tokens.Relation LIKE 'genitive%'
            OR checked_relation_tokens.Relation LIKE 'direct object%'
            OR checked_relation_tokens.Relation LIKE 'argument of adjective%'
            OR checked_relation_tokens.Relation LIKE 'accusative%'
            OR checked_relation_tokens.Relation LIKE 'indirect object%'
            OR checked_relation_tokens.Relation LIKE 'dative%'
            OR checked_relation_tokens.Relation = 'interjection, vocative'
            OR checked_relation_tokens.Relation = 'modifier of nominal, nominal'
            OR checked_relation_tokens.Relation LIKE 'modifier of verb%nominal'
            OR checked_relation_tokens.Relation = 'object of preposition'
            OR checked_relation_tokens.Relation LIKE 'subject of infinitive%'
            OR checked_relation_tokens.Relation = 'resumptive pronoun'),
     nominal_types_head AS
     (SELECT 'NominalType' AS TypeName, 'head' AS HeadOrDep, head.SentenceID,
             head.SentencePosition, dep.SentencePosition AS OtherPosition,
             checked_relation_tokens.Relation, 1 AS CheckOrder
      FROM gnt.checked_relation_tokens
           JOIN gnt.words head
           ON checked_relation_tokens.SentenceID = head.SentenceID
              AND checked_relation_tokens.HeadPos = head.SentencePosition
           JOIN gnt.words dep
           ON checked_relation_tokens.SentenceID = dep.SentenceID
              AND checked_relation_tokens.DependentPos = dep.SentencePosition
      WHERE checked_relation_tokens.Relation LIKE 'argument of adjective%'
            OR checked_relation_tokens.Relation LIKE 'negation%nominal'
            OR checked_relation_tokens.Relation LIKE 'determiner%'
            OR checked_relation_tokens.Relation LIKE 'modifier of nominal%'),
     case_types_dep AS
     (SELECT 'CaseType' AS TypeName, 'dep' AS HeadOrDep, dep.SentenceID,
             dep.SentencePosition, head.SentencePosition AS OtherPosition,
             checked_relation_tokens.Relation, 2 AS CheckOrder
      FROM gnt.checked_relation_tokens
           JOIN gnt.words head
           ON checked_relation_tokens.SentenceID = head.SentenceID
              AND checked_relation_tokens.HeadPos = head.SentencePosition
           JOIN gnt.words dep
           ON checked_relation_tokens.SentenceID = dep.SentenceID
              AND checked_relation_tokens.DependentPos = dep.SentencePosition
      WHERE checked_relation_tokens.Relation LIKE 'subject of infinitive%'
            OR checked_relation_tokens.Relation LIKE 'genitive%'
            OR checked_relation_tokens.Relation LIKE 'direct object%'
            OR checked_relation_tokens.Relation LIKE 'accusative%'
            OR checked_relation_tokens.Relation LIKE 'indirect object%'
            OR checked_relation_tokens.Relation LIKE 'dative%'
            OR checked_relation_tokens.Relation = 'interjection, vocative'
            OR checked_relation_tokens.Relation = 'predicate, nominal'
            OR checked_relation_tokens.Relation = 'argument of adjective, nominal'
            OR checked_relation_tokens.Relation = 'object of preposition'
            OR checked_relation_tokens.Relation = 'resumptive pronoun'),
     case_types_head AS
     (SELECT 'CaseType' AS TypeName, 'head' AS HeadOrDep, head.SentenceID,
             head.SentencePosition,
             checked_relation_tokens.DependentPos AS OtherPosition,
             checked_relation_tokens.Relation, 2 AS CheckOrder
      FROM gnt.checked_relation_tokens
           JOIN gnt.words head
           ON checked_relation_tokens.SentenceID = head.SentenceID
              AND checked_relation_tokens.HeadPos = head.SentencePosition
      WHERE checked_relation_tokens.Relation LIKE 'negation%nominal'
            OR checked_relation_tokens.Relation = 'infinitive argument of noun')
SELECT TypeName, HeadOrDep, SentenceID, SentencePosition, OtherPosition,
       Relation, CheckOrder
FROM (SELECT * FROM nominal_types_dep
      UNION
      SELECT * FROM nominal_types_head
      UNION
      SELECT * FROM case_types_dep
      UNION
      SELECT * FROM case_types_head) all_types;
