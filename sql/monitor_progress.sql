CREATE OR REPLACE VIEW monitor_progress AS
WITH progress AS
     (SELECT relations.Relation, COUNT(*) AS Total,
             SUM(CASE WHEN checked_relation_tokens.SentenceID IS NULL THEN 0
                      ELSE 1
                 END) AS Checked,
             ROUND(SUM(CASE WHEN checked_relation_tokens.SentenceID IS NULL THEN 0
                            ELSE 100
                       END) / COUNT(*), 1) AS Percent
      FROM relations
           LEFT JOIN checked_relation_tokens
           ON relations.SentenceID = checked_relation_tokens.SentenceID
              AND relations.HeadPos = checked_relation_tokens.HeadPos
              AND relations.DependentPos = checked_relation_tokens.DependentPos
              AND relations.Relation = checked_relation_tokens.Relation
      GROUP BY relations.Relation WITH ROLLUP)
SELECT COALESCE(Relation, '--- TOTAL ---') AS Relation, Total, Checked, Percent
FROM progress
ORDER BY CASE WHEN Relation IS NULL THEN 1
              ELSE 0
         END, Relation;
