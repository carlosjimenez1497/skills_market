import sqlite3

conn = sqlite3.connect("jobs.db")
for row in conn.execute("SELECT id, company, title, location , job_view_url FROM jobs"):
    print(row)
conn.close()

# for row in conn.execute("SELECT id, description FROM jobs"):
#     print(row)
# conn.close()