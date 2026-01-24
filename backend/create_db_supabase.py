import os
from app.db import engine
from app.models import Base  # assuming you have Base in models.py

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Tables created.")
