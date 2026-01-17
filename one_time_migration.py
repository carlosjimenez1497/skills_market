import sqlite3

conn = sqlite3.connect("jobs.db")
cur = conn.cursor()

cur.execute("""
ALTER TABLE jobs ADD COLUMN job_view_url TEXT
""")

conn.commit()
conn.close()

print("Migration applied ✔")