CREATE OR REPLACE VIEW monitor_progress AS
SELECT relations.Relation, COUNT(*) AS Total,
       SUM(CASE WHEN checked_relation_tokens.SentenceID IS NULL THEN 0
                ELSE 1
           END) AS Checked
FROM relations
     LEFT JOIN checked_relation_tokens
     ON relations.SentenceID = checked_relation_tokens.SentenceID
        AND relations.HeadPos = checked_relation_tokens.HeadPos
        AND relations.DependentPos = checked_relation_tokens.DependentPos
        AND relations.Relation = checked_relation_tokens.Relation
GROUP BY relations.Relation
ORDER BY relations.Relation;
