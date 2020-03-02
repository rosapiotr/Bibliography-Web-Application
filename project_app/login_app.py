from flask import Flask, request, jsonify
import redis
from flask_jwt_extended import JWTManager, create_access_token
import os
import hashlib
from werkzeug.utils import cached_property
from flask_restplus import Api, Resource, fields
from flask_cors import CORS, cross_origin

SECRET_KEY = "PROJECT_SECRET"
TOKEN_EXPIRES_IN_SECONDS = 180
ACCESS_TOKEN = "access_token_cookie"

app = Flask(__name__, static_url_path = "")
api_app = Api(app = app, version = "0.1", title = "Project app API", description = "REST-full API for library", doc="/api")

db = redis.Redis(host = "redis", port = 6379, decode_responses = True)
app.secret_key = os.environ.get(SECRET_KEY)

app.config["JWT_SECRET_KEY"] = os.environ.get(SECRET_KEY)
app.config["JWT_TOKEN_LOCATION"] = ["cookies", "headers"]
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = TOKEN_EXPIRES_IN_SECONDS
jwt = JWTManager(app)
CORS(app)

login_namespace = api_app.namespace("api/log", description = "Login API")
registration_namespace = api_app.namespace("api/register", description = "Registration API")
user_namespace = api_app.namespace("api/user", description = "User API")

@user_namespace.route("/<string:username>")
class User(Resource):
    def __init__(self, args):
        super().__init__(args)
    
    new_user_model = api_app.model("User model",
        {
            "login": fields.String(required = True, description = "Login", help = "Login cannot be null", example = "login")
        })

    def get(self, username):
        username = username.encode("utf-8")
        username_hash = hashlib.sha512(username).hexdigest()
        if not db.get(username_hash):
            message = {"status": 404, "message": "Not Found " + request.url}
            resp = jsonify(message)
            resp.status_code = 404
        else:
            message = {"status": 200, "message": "OK"}
            resp = jsonify(message)
            resp.status_code = 200
        return resp

@login_namespace.route("")
class Login(Resource):
    def __init__(self, args):
        super().__init__(args)

    new_log_model = api_app.model("Log model",
        {
            "login": fields.String(required = True, description = "Login", help = "Login cannot be null", example = "login"),
            "password": fields.String(required = True, description = "Password", help = "Password cannot be null", example = "password")
        })

    @api_app.expect(new_log_model)
    @cross_origin()
    def post(self):
        app.logger.debug(request.json["login"])
        username_p = request.json["login"]
        username = username_p.encode("utf-8")
        password = request.json["password"].encode("utf-8")
        username_hash = hashlib.sha512(username).hexdigest()
        if not db.get(username_hash):
            return { "status": 401, "message": "Niepoprawna nazwaw użytkownika" } 
        else:
            secret_username_hash = db.get(username_hash)
            if hashlib.sha512(password).hexdigest() == db.hgetall(secret_username_hash)["Password"]:
                access_token = create_access_token(identity = username_p)
                return {"access_token": access_token}
            else:
                return { "status": 401, "message": "Niepoprawne hasło" } 

@registration_namespace.route("")
class Registration(Resource):
    def __init__(self, args):
        super().__init__(args)

    new_register_model = api_app.model("Register model",
        {
            "firstname": fields.String(required = True, description = "Your first name", help = "First name cannot be null", example = "Piotr"),
            "lastname": fields.String(required = True, description = "Your last name", help = "Last name cannot be null", example = "Rosa"),
            "login": fields.String(required = True, description = "Your login", help = "Login cannot be null", example = "login"),
            "password": fields.String(required = True, description = "Password for your account", help = "Password name cannot be null", example = "password"),
            "password_r": fields.String(required = True, description = "Repeat password", help = "Passwords must be the same", example = "password")
        })

    @api_app.expect(new_register_model)
    def post(self):
        firstname = request.json["firstname"].encode("utf-8")
        lastname = request.json["lastname"].encode("utf-8")
        username = request.json["login"].encode("utf-8")
        password = request.json["password"].encode("utf-8")
        password_r = request.json["password_r"].encode("utf-8")
        if password == password_r:
            username_hash = hashlib.sha512(username).hexdigest()
            password_hash = hashlib.sha512(password).hexdigest()
            secret_username = username + os.urandom(16)
            secret_username_hash = hashlib.sha512(secret_username).hexdigest()
            if not db.get(username_hash):
                user = {"Name":firstname, "Surname":lastname, "Login":username, "Password": password_hash}
                db.set(username_hash, secret_username_hash)
                db.hmset(secret_username_hash, user)
                return {"status": 200, "message": "Dodano nowego użytkownika"}
            else:
                return {"status": 409, "message": "Użytkownik już istnieje"}
        else:
            return {"status": 422, "message": "Hasła nie są takie same"}