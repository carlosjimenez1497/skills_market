-- SQLite
SELECT company, title, COUNT(*) AS cnt
FROM jobs
GROUP BY company, title
HAVING cnt > 1
ORDER BY cnt DESC;