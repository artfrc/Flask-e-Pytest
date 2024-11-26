from datetime import datetime
from flask import Flask, jsonify, request
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from database import db
from models.user import User
from models.meal import Meal
from models.user_meal import UserMeal

app = Flask(__name__)

app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
login_manager = LoginManager()

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
  return User.query.get(user_id)

@app.route('/login', methods=['POST'])
def login():
  data = request.json
  username = data.get("username")
  password = data.get("password")
  
  user = User.query.filter_by(username=username).first()
  
  if user and user.password == password:
    login_user(user)
    return jsonify({'message': f'Usuário {username} autenticado com sucesso.'})
    
  return jsonify({'message': 'Credenciais invaliidas.'}), 400

@app.route('/logout', methods=['GET'])
@login_required
def logout():
  logout_user()
  return jsonify({'message': 'Logout realizado com sucesso.'})

@app.route('/user', methods=['POST'])
def create_user():
  data = request.json
  username = data.get('username')
  pw = data.get('password')
  role = data.get('role')

  errors = {
        'username': 'Envie um username.',
        'password': 'Envie uma password.'
    }
  error_messages = []
  
  if not username:
    error_messages.append(errors['username'])
    
  if not pw:
    error_messages.append(errors['password'])
  
  if error_messages:
      return jsonify({'message': 'Erro: ' + ' '.join(error_messages)}), 400
  
  else:
    user = User(username=username, password=pw, role=role)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'Usuário cadastrado com sucesso.'})
  
@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
  user = User.query.get(user_id)
  
  if user:
    return jsonify({
      'username': user.username,
      'role': user.role
    })
    
  return jsonify({'message': 'Usuário não encontrado.'}), 404

@app.route('/users', methods=['GET'])
def get_users():
  users = User.query.all()
  
  if not users:
    return jsonify({'message': 'Nenhum usuário encontrado.'})
  
  users_list = []
  for user in users:
    users_list.append({
      'id': user.id,
      'username': user.username,
      'role': user.role
    })
    
  return jsonify(users_list)

@app.route('/user/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
  user = User.query.get(user_id)
  
  errors = {
    'nothing_user': 'Usuário não encontrado.',
    'permission_denied': 'permissão negada.'
  }
  
  error_messages = []
  
  if not user:
    error_messages.append(errors['nothing_user'])
  
  if user_id != current_user.id and current_user.role == 'user':
    error_messages.append(errors['permission_denied'])
  
  if error_messages:
    return jsonify({'message': 'Erro: ' + ' '.join(error_messages)}), 400
  
  data = request.json
  username = data.get('username')
  if username:
    user.username = username
  db.session.commit()
  
  return jsonify({'message': 'Usuário atualizado com sucesso.'})

@app.route('/user/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
  user = User.query.get(user_id)
  errors = {
    'nothing_user': 'Usuário não encontrado.',
    'permission_denied': 'permissão negada.'
  }
  
  error_messages = []
  
  if not user:
    error_messages.append(errors['nothing_user'])
    
  if user_id == current_user.id:
    error_messages.append(errors['permission_denied'])
  
  if error_messages:
    return jsonify({'message': 'Erro: ' + ' '.join(error_messages)})
  
  db.session.delete(user)
  db.session.commit()
  return jsonify({'message': 'Usuário deletado com sucesso.'})

@app.route('/meal', methods=['POST'])
def create_meal():
  data = request.json
  name = data.get('name')
  description = data.get('description')
  
  meal = Meal(name=name,description=description)
  
  db.session.add(meal)
  db.session.commit()
  
  return jsonify({'message': 'Refeição adicionadaa com sucesso.'})

@app.route('/meal/<int:meal_id>', methods=['GET'])
def get_meal(meal_id):
  meal = Meal.query.get(meal_id)
  
  if meal:
    return jsonify({
      'id': meal.id,
      'name': meal.name,
      'description': meal.description
    })
    
  return jsonify({'message': 'Refeição não encontrada.'}), 404

@app.route('/meals', methods=['GET'])
def get_meals():
  meals = Meal.query.all()
  
  if not meals:
    return jsonify({'message': 'Nenhuma refeição encontrada.'})
  
  meals_list = []
  for meal in meals:
    meals_list.append({
      'id': meal.id,
      'name': meal.name,
      'description': meal.description
    })
    
  return jsonify(meals_list)

@app.route('/meal/<int:meal_id>', methods=['PUT'])
@login_required
def update_meal(meal_id):
  meal = Meal.query.get(meal_id)
  
  errors = {
    'nothing_meal': 'Refeição não encontrada.',
    'permission_denied': 'permissão negada.'
  }
  
  error_messages = []
  
  if not meal:
    error_messages.append(errors['nothing_meal'])
    
  if current_user.role != 'admin':
    error_messages.append(errors['permission_denied'])
  
  if error_messages:
    return jsonify({'message': 'Erro: ' + ' '.join(error_messages)}), 404
  
  data = request.json
  name = data.get('name')
  
  if name:
    meal.name = name
  
  description = data.get('description') 
  
  if description:
    meal.description = description
  
  db.session.commit()
  
  return jsonify({
    'id': meal.id,
    'name': meal.name,
    'description': meal.description,
    'message': 'Refeição atualizada com sucesso.'})

@app.route('/meal/<int:meal_id>', methods=['DELETE'])
@login_required
def delete_meal(meal_id):
  meal = Meal.query.get(meal_id)
  errors = {
    'nothing_meal': 'Refeição não encontrada.',
    'permission_denied': 'permissão negada.'
  }
  
  error_messages = []
  
  if not meal:
    error_messages.append(errors['nothing_meal'])
    
  if current_user.role != 'admin':
    error_messages.append(errors['permission_denied'])
  
  if error_messages:
    return jsonify({'message': 'Erro: ' + ' '.join(error_messages)})
  
  db.session.delete(meal)
  db.session.commit()
  return jsonify({'message': 'Refeição deletada com sucesso.'})

@app.route('/add_user_meal/<int:user_id>/<int:meal_id>', methods=['POST'])
def add_user_meal(user_id, meal_id):
    user = User.query.get(user_id)
    meal = Meal.query.get(meal_id)
    
    if not user or not meal:
      return jsonify({'message': 'Usuário ou refeição não encontrado.'}), 404
    
    now = datetime.now()
    formatted_date = now.strftime("%d-%m-%Y %H:%M:%S")
    
    user_meal = UserMeal(
      user_id=user_id,
      meal_id=meal_id,
      date=formatted_date
    )
    
    data = request.json
    diet = data.get('diet')
    if diet is not None:
      user_meal.diet = diet
    
    db.session.add(user_meal)
    db.session.commit()
    return jsonify({'message': f'Refeição adicionada com sucesso ao usuário {user.username}.'})
    
      

if (__name__) == '__main__':
  app.run(debug=True)