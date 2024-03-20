from flask import request
from flask import jsonify
import flask_login
from flask_login import login_user
from uni_rlhf.models import db, User
from uni_rlhf.config import app, db,  celery
from flask import jsonify
from uni_rlhf.controllers.project import project_blueprint
from uni_rlhf.controllers.query import query_blueprint
from uni_rlhf.controllers.annotate import annotate_blueprint
from uni_rlhf.dataset_validator.user_validator import user_schema
from jsonschema import validate, ValidationError


app.register_blueprint(project_blueprint, url_prefix='/project')
app.register_blueprint(query_blueprint, url_prefix='/query')
app.register_blueprint(annotate_blueprint, url_pref='/annotate')


@app.route('/')
def loginpage():  
    conn = db.session.connection()
    return jsonify({'message':'success'})


@app.route('/login', methods=['POST'])
def login():
    """
    Authenticates a user and initiates a login session.
    Args:
        - None: Extracts 'username' and 'password' from request JSON.
    Returns:
        - jsonify: Dictionary containing 'message' and 'username' if successful, or 'message' if failed.
    Raises:
        - None: Function execution does not explicitly raise exceptions.
    """
    username = request.json.get('username')
    password = request.json.get('password')

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        login_user(user)  
        return jsonify({'message': 'login success', 'username': username})
    else:
        return jsonify({'message': 'Invalid username or password'})

    
@app.route('/register', methods=['POST'])
def register():
    """
    Registers a new user with provided credentials.
    Args:
        - None: Extracts 'username', 'password', and 'email' from request JSON.
    Returns:
        - jsonify: Dictionary containing 'message' indicating registration success or failure.
    Raises:
        - 409: If the username already exists.
    """
    try:
        data = request.json
        validate(instance=data, schema=user_schema)
    except ValidationError as e:
        return jsonify({'error': 'Invalid data', 'message': str(e)}), 400

    username = request.json.get('username')
    password = request.json.get('password')
    email = request.json.get('email')

    existing_user = User.query.filter_by(username=username).first()

    if existing_user:
        return jsonify({'message': 'Username already exists'}), 409

    new_user = User(username=username, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201


@app.route("/logout")
def logout():
    """
    Logs out the current user and ends the session.
    Args:
        - None
    Returns:
        - str: Confirmation message of successful logout.
    Raises:
        - None: Function execution does not explicitly raise exceptions.
    """
    flask_login.logout_user()
    return "Logged out"


if __name__ == '__main__':
    app.run(port=8502)
