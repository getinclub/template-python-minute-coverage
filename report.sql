-- Repair this reporting query. Keep the schema and harness unchanged.
SELECT o.asset AS asset,
       (o.observed_second / 60) * 60 AS minute_start,
       COUNT(*) AS covered_seconds,
       60 AS expected_seconds,
       CASE WHEN COUNT(*) >= 60 THEN 'HEALTHY' ELSE 'GAP' END AS status
FROM observations AS o
JOIN expected_assets AS a ON a.asset = o.asset
CROSS JOIN report_window AS w
WHERE o.valid = 1
  AND o.observed_second >= w.start_second
  AND o.observed_second < w.end_second
GROUP BY o.asset, (o.observed_second / 60) * 60
ORDER BY o.asset COLLATE BINARY, minute_start;
