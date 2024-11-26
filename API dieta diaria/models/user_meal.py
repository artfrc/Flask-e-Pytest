from sqlalchemy import ForeignKey
from database import db

class UserMeal(db.Model):
  id = db.Column(db.Integer,primary_key=True)
  user_id = db.Column(db.Integer, ForeignKey('user.id'))
  meal_id = db.Column(db.Integer, ForeignKey('meal.id'))
  date = db.Column(db.String(20), nullable=True)
  diet = db.Column(db.Boolean, nullable=True, default=True)
  
  user = db.relationship('User', backref='user_meals', lazy=True)
  meal = db.relationship('Meal', backref='user_meals', lazy=True)