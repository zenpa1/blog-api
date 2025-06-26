# -- python check_db.py to check database --
from app.database import SessionLocal
from app import models

db = SessionLocal()
print("Posts:", db.query(models.Post).all())
print("Users:", db.query(models.User).all())
db.close()