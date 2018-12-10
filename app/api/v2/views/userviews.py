import psycopg2
from flask_restful import Resource
from flask import request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
import datetime
from app.api.v2.models.usermodels import UserModels
from db_config import *


class Users(Resource):
    def __init__(self):
        self.db = UserModels()

    def post(self):
        data = request.get_json()
        first_name = data['first_name']
        last_name = data['last_name']
        username = data['username']
        email = data['email']
        phonenumber = data['phonenumber']
        date_created = datetime.datetime.now()
        password = data['password']
        confirm_password = data['confirm_password']

        resp = None
        if password.isspace() or len(password.strip()) < 8:
            resp = {'Message': 'Please fill in a valid password!'}
        if email.isspace() or not self.db.validate_email(email):
            resp = {'Message': 'Please enter a valid email!'}
        if first_name.isspace():
            resp = {'Message': 'Please enter a first name!'}
        if last_name.isspace():
            resp = {'Message': 'Please enter a last name!'}
        if username.isspace():
            resp = {'Message': 'Please enter a username!'}

        if resp is not None:
            return jsonify(resp)

        user = self.db.get_user_name(username)
        emailconfirm = self.db.get_email(email)

        if user:
            return jsonify({'Message': 'Username already exists!'})
        if emailconfirm:
            return jsonify({'Message': 'Email already exists!'})
        if password != confirm_password:
            return jsonify({'Message': 'Password already exists!'})

        self.db.save_user(first_name, last_name, username,
                          email, phonenumber, password)
        return jsonify({'Message': 'User saved successfully'}, 201)

    def get(self):
        result = self.db.get_all()
        if result == []:
            return self.notFound()
        else:
            return make_response(jsonify(
                {
                    'Message': 'Records returned successfully',
                    'Data': result
                }
            ), 200)


class Login(Resource):
    def __init__(self):
        self.db = UserModels()

    def post(self):
        data = request.get_json()
        username = data['username']
        password = generate_password_hash(data['password'])
        user = self.db.get_user_name(username)

        if username.isspace() or password.isspace():
            return jsonify({'Message': 'Please provide all credentials!'})

        if password.isspace() or password is None:
            return jsonify({'Message': 'Please enter a valid password!'})

        if not user:
            return jsonify({'Message': 'No user found'}, 404)

        if not self.db.check_password(username, password):
            return jsonify({'Message': 'Wrong password!'})

        login_token = self.db.user_login(username)
        if login_token:
            return jsonify({
                'Message': 'You are now logged in!',
                'Token': login_token
            }, 200)
