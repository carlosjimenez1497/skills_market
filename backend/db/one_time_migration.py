import sqlite3

conn = sqlite3.connect("db/jobs.db")
cur = conn.cursor()

# cur.execute("""
# ALTER TABLE jobs ADD COLUMN job_view_url TEXT
# """)

# cur.execute("""
# ALTER TABLE jobs ADD COLUMN job_id TEXT
# """)

# cur.execute("""
# --ALTER TABLE jobs ADD COLUMN language_code TEXT;
# ALTER TABLE jobs ADD COLUMN language_confidence REAL;
# """)

conn.commit()
conn.close()

print("Migration applied ✔")