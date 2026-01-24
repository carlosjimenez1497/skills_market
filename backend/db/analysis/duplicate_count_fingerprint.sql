SELECT company, title, location, COUNT(*) AS cnt
FROM jobs
GROUP BY company, title, location
HAVING cnt > 1
ORDER BY cnt DESC;