from database import db

class Meal(db.Model):
  id = db.Column(db.Integer,primary_key=True)
  name = db.Column(db.String(40), unique=True, nullable=False)
  description = db.Column(db.String(120), nullable=True)