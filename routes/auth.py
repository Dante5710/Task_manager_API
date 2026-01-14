from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from models import db, User
from marshmallow import Schema, fields, validate

auth_bp = Blueprint('auth', __name__)

# Validation Schema for Auth
class AuthSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    password = fields.Str(required=True, validate=validate.Length(min=6))

auth_schema = AuthSchema()

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    errors = auth_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "User already exists"}), 400

    hashed_pw = generate_password_hash(data['password'])
    new_user = User(username=data['username'], password=hashed_pw)
    
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()
    
    if user and check_password_hash(user.password, data.get('password')):
        access_token = create_access_token(identity=str(user.id))
        return jsonify(access_token=access_token), 200
    
    return jsonify({"error": "Invalid username or password"}), 401
