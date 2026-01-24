SELECT job_view_url, COUNT(*) AS cnt
FROM jobs
GROUP BY job_view_url
HAVING cnt > 1
ORDER BY cnt DESC;