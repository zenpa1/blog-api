# -- python reset_db.py to reset database --
from app.database import engine
from app import models

def reset_database():
    print("Dropping all tables...")
    models.Base.metadata.drop_all(bind=engine)
    print("Creating all tables...")
    models.Base.metadata.create_all(bind=engine)
    print("Database reset complete!")

if __name__ == "__main__":
    reset_database()