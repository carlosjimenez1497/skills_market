-- SQLite
SELECT company, COUNT(*) AS cnt
FROM jobs
GROUP BY company
ORDER BY cnt DESC
LIMIT 20;}