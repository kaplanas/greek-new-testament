CREATE OR REPLACE VIEW monitor_progress AS
WITH type_dep AS
     (SELECT required_types.SentenceID,
             required_types.SentencePosition AS DependentPos,
             required_types.Relation,
             CONCAT(required_types.SentencePosition, '-',
                    required_types.TypeName) AS TypeNeededID,
             CASE WHEN required_types.TypeName = 'NominalType'
                       AND checked_types.NominalType IS NOT NULL
                       THEN 1
                  WHEN required_types.TypeName = 'NominalType'
                       THEN 0
                  WHEN required_types.TypeName = 'NounClassType'
                       AND checked_types.NounClassType IS NOT NULL
                       THEN 1
                  WHEN required_types.TypeName = 'NounClassType'
                       THEN 0
                  WHEN required_types.TypeName = 'CaseType'
                       AND checked_types.CaseType IS NOT NULL
                       THEN 1
                  WHEN required_types.TypeName = 'CaseType'
                       THEN 0
                  WHEN required_types.TypeName = 'VerbClassType'
                       AND checked_types.VerbClassType IS NOT NULL
                       THEN 1
                  WHEN required_types.TypeName = 'VerbClassType'
                       THEN 0
             END AS Checked
      FROM gnt.required_types
           LEFT JOIN gnt.checked_types
           ON required_types.SentenceID = checked_types.SentenceID
              AND required_types.SentencePosition = checked_types.SentencePosition
      WHERE required_types.HeadOrDep = 'dep'),
     type_head AS
     (SELECT required_types.SentenceID, checked_relation_tokens.DependentPos,
             required_types.Relation,
             CONCAT(required_types.SentencePosition, '-',
                    required_types.TypeName) AS TypeNeededID,
             CASE WHEN required_types.TypeName = 'NominalType'
                       AND checked_types.NominalType IS NOT NULL
                       THEN 1
                  WHEN required_types.TypeName = 'NominalType'
                       THEN 0
                  WHEN required_types.TypeName = 'NounClassType'
                       AND checked_types.NounClassType IS NOT NULL
                       THEN 1
                  WHEN required_types.TypeName = 'NounClassType'
                       THEN 0
                  WHEN required_types.TypeName = 'CaseType'
                       AND checked_types.CaseType IS NOT NULL
                       THEN 1
                  WHEN required_types.TypeName = 'CaseType'
                       THEN 0
                  WHEN required_types.TypeName = 'VerbClassType'
                       AND checked_types.VerbClassType IS NOT NULL
                       THEN 1
                  WHEN required_types.TypeName = 'VerbClassType'
                       THEN 0
             END AS Checked
      FROM gnt.required_types
           JOIN gnt.checked_relation_tokens
           ON required_types.SentenceID = checked_relation_tokens.SentenceID
              AND required_types.SentencePosition = checked_relation_tokens.HeadPos
              AND required_types.Relation = checked_relation_tokens.Relation
           LEFT JOIN gnt.checked_types
           ON required_types.SentenceID = checked_types.SentenceID
              AND required_types.SentencePosition = checked_types.SentencePosition
      WHERE required_types.HeadOrDep = 'head'),
     all_types AS
     (SELECT SentenceID, DependentPos, Relation, TypeNeededID, Checked
      FROM type_dep
      UNION
      SELECT SentenceID, DependentPos, Relation, TypeNeededID, Checked
      FROM type_head),
     type_counts AS
     (SELECT SentenceID, DependentPos, Relation,
             COUNT(DISTINCT TypeNeededID) AS TypeTotal,
             SUM(Checked) AS TypeN
      FROM all_types
      GROUP BY SentenceID, DependentPos, Relation),
     progress AS
     (SELECT relations.Relation, COUNT(*) AS RelTotal,
             SUM(CASE WHEN checked_relation_tokens.SentenceID IS NULL
                           THEN 0
                      ELSE 1
                 END) AS RelN,
             ROUND(AVG(CASE WHEN checked_relation_tokens.SentenceID IS NULL
                                 THEN 0
                            ELSE 100
                       END), 1) AS RelP,
             LPAD(COALESCE(SUM(type_counts.TypeTotal), ''),
                  9, ' ') AS TypeTotal,
             LPAD(COALESCE(SUM(type_counts.TypeN), ''), 6, ' ') AS TypeN,
             LPAD(COALESCE(ROUND((SUM(type_counts.TypeN) /
                                  SUM(type_counts.TypeTotal)) * 100, 1),
                           ''),
                  5, ' ') AS TypeP
      FROM gnt.relations
           LEFT JOIN gnt.checked_relation_tokens
           ON relations.SentenceID = checked_relation_tokens.SentenceID
              AND relations.HeadPos = checked_relation_tokens.HeadPos
              AND relations.DependentPos = checked_relation_tokens.DependentPos
              AND relations.Relation = checked_relation_tokens.Relation
           LEFT JOIN type_counts
           ON relations.SentenceID = type_counts.SentenceID
              AND relations.DependentPos = type_counts.DependentPos
              AND relations.Relation = type_counts.Relation
      GROUP BY relations.Relation WITH ROLLUP)
SELECT COALESCE(Relation, '--- TOTAL ---') AS Relation, RelTotal, RelN, RelP,
       TypeTotal, TypeN, TypeP
FROM progress
ORDER BY CASE WHEN Relation IS NULL THEN 1
              ELSE 0
         END, Relation;
