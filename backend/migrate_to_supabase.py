import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import your model
from app.models import Job, Base

SQLITE_URL = "sqlite:///db/jobs.db"
PG_URL = os.environ["DATABASE_URL"]  # Supabase

sqlite_engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
pg_engine = create_engine(PG_URL, pool_pre_ping=True)

SQLiteSession = sessionmaker(bind=sqlite_engine, autoflush=False, autocommit=False)
PgSession = sessionmaker(bind=pg_engine, autoflush=False, autocommit=False)

def main():
    # Ensure tables exist in Postgres
    Base.metadata.create_all(bind=pg_engine)

    s_src = SQLiteSession()
    s_dst = PgSession()

    try:
        jobs = s_src.query(Job)
        jobs_2 = jobs.order_by(Job.id.asc()).all()
        print(f"Found {len(jobs_2)} jobs in SQLite")

        # Insert in Postgres
        # We’ll keep the same IDs to preserve ordering (optional)
        for j in jobs:
            s_dst.merge(Job(
                id=j.id,
                source=j.source,
                source_url=j.source_url,
                job_id=j.job_id,
                job_view_url=j.job_view_url,
                company=j.company,
                title=j.title,
                location=j.location,
                description=j.description,
                fingerprint=j.fingerprint,
                language_code=j.language_code,
                first_seen=j.first_seen,
                last_seen=j.last_seen,
                times_seen=j.times_seen,
                created_at=j.created_at,
                updated_at=j.updated_at,
            ))

        s_dst.commit()
        print("Migration complete ✅")

    finally:
        s_src.close()
        s_dst.close()

if __name__ == "__main__":
    main()
