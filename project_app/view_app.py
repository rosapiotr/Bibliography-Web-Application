from flask import Flask, request, render_template, url_for, make_response, abort, redirect, flash, send_file
import redis
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import os
import requests

GET = "GET"
POST = "POST"
SECRET_KEY = "PROJECT_SECRET"
TOKEN_EXPIRES_IN_SECONDS = 180
ACCESS_TOKEN = "access_token_cookie"
REGISTER_URL = "https://web:80/api/register"
LOG_URL = "https://web:80/api/log"
PUBLICATION_LIST_URL = "https://web-files:81/api/publication/list"
FILE_LIST_URL = "https://web-files:81/api/file/list"
PUBLICATION_URL = "https://web-files:81/api/publication/"
FILE_URL = "https://web-files:81/api/file/"

app = Flask(__name__, static_url_path = "")
db = redis.Redis(host = "redis", port = 6379, decode_responses = True)

app.config["JWT_SECRET_KEY"] = os.environ.get(SECRET_KEY)
app.config["JWT_TOKEN_LOCATION"] = ["cookies", "headers"]
app.config["JWT_COOKIE_CSRF_PROTECT"] = False
app.secret_key = os.environ.get(SECRET_KEY)

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = TOKEN_EXPIRES_IN_SECONDS
jwt = JWTManager(app)

@jwt.unauthorized_loader
def unauthorized_access(unauthorized_callback):
    return render_template("errors/403.html")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/registration")
def registration():
    return render_template("registration.html")

@app.route("/register", methods = [POST])
def register():
    firstname = request.form["firstname"]
    lastname = request.form["lastname"]
    username = request.form["login"]
    password = request.form["password"]
    password_r = request.form["repeat-password"]
    data = {
        "firstname": firstname,
        "lastname": lastname,
        "login": username,
        "password": password,
        "password_r": password_r
    }
    url = REGISTER_URL
    resp = requests.post(url, json=data, verify=False)
    if resp.json()["status"] == 200:
        return redirect(url_for(("login")))
    else:
        return redirect(url_for("registration.html"))

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/log", methods = [POST])
def log():
    data = {
        "login": request.form["login"],
        "password": request.form["password"]
    }
    url = LOG_URL
    resp = requests.post(url, json=data, verify=False)
    try:
        access_token = resp.json()["access_token"]
        response = make_response(redirect(url_for("index")))
        response.set_cookie(ACCESS_TOKEN, access_token, max_age = 180, secure = True, httponly = True)
        return response
    except Exception as e:
        if resp.json()["message"] == "Niepoprawne hasło":
            flash("Niepoprawne hasło")
            return redirect(url_for("login"))
        else:
            flash("Niepoprawny login")
            return redirect(url_for("login"))

@app.route("/logout")
def logout():
    response = make_response(redirect(url_for("login")))
    response.set_cookie(ACCESS_TOKEN, expires=0)
    return response

@app.route("/publications", methods=[GET])
def publications():
    return render_template("publications.html")

@app.route("/my_publications")
@jwt_required
def my_publications():
    access_token = create_access_token(get_jwt_identity())
    headers = {
        "Authorization": "Bearer " + access_token
    }
    url = PUBLICATION_LIST_URL
    resp = requests.get(url, verify=False, headers=headers)
    response = make_response(render_template("my_publications.html", data = resp.json()))
    response.set_cookie("access_token_cookie", access_token, max_age = 180, secure = True, httponly = True)
    return response

@app.route("/post_publication", methods=[POST])
@jwt_required
def publish():
    title = request.form["title"]
    year = request.form["year"]
    author = request.form["author"]
    data = {
        "title": title,
        "year": year,
        "author": author
    }
    url = PUBLICATION_LIST_URL
    access_token = create_access_token(get_jwt_identity())
    headers = {
        "Authorization": "Bearer " + access_token
    }
    resp = requests.post(url, json=data, verify=False, headers = headers)
    if resp.status_code == 409:
        flash("Publiakcja istnieje")
    elif resp.status_code == 400:
        flash("Coś poszło nie tak, spróbuj ponownie.")
    response = make_response(redirect(url_for("my_publications")))
    response.set_cookie("access_token_cookie", access_token, max_age = 180, secure = True, httponly = True)
    return response

@app.route("/publication/<int:id>", methods=[GET])
@jwt_required
def publication(id):
    try:
        access_token = create_access_token(get_jwt_identity())
        headers = {
            "Authorization": "Bearer " + access_token
        }
        url = PUBLICATION_URL + str(id)
        resp = requests.get(url, verify=False, headers=headers)
        next_url = ""
        previous_url = ""
        if resp.json()["next"] != "":
            next_url = "https://localhost:82/publication/" + resp.json()["next"].rsplit("/", 1)[1]
        if resp.json()["previous"] != "":
            previous_url = "https://localhost:82/publication/" + resp.json()["previous"].rsplit("/", 1)[1]
        response = make_response(render_template("publication_details.html", data = resp.json(), previous_url=previous_url, next_url=next_url))
        response.set_cookie("access_token_cookie", access_token, max_age = 180, secure = True, httponly = True)
        return response
    except Exception as e:
        abort(404)

@app.route("/delete_publication/<int:id>")
@jwt_required
def deletepub(id):
    username = get_jwt_identity()
    access_token = create_access_token(username)
    url = PUBLICATION_URL + str(id)
    headers = {
        "Authorization": "Bearer " + access_token
    }
    resp = requests.delete(url, verify=False, headers = headers)
    if resp.status_code == 200:
        response = make_response(redirect(url_for("my_publications")))
        response.set_cookie("access_token_cookie", access_token, max_age = 180, secure = True, httponly = True)
        return response
    else:
        abort(400)

@app.route("/attachfile/<int:pub_ID>", methods=[POST])
@jwt_required
def attachfile(pub_ID):
    username = get_jwt_identity()
    access_token = create_access_token(username)
    file_id = request.form["file_ID"]
    url = PUBLICATION_URL + str(pub_ID)
    headers = {
        "Authorization": "Bearer " + access_token
    }
    data = {
        "file_id": file_id
    }
    resp = requests.put(url, verify=False, json=data, headers = headers)
    if resp.json()["status"] == 200 or resp.json()["status"] == 204:
        return redirect(url_for("publication", id=pub_ID))
    elif resp.json()["status"] == 404:
        flash("Plik o podanym ID nie istnieje")
        return redirect(url_for("publication", id=pub_ID))
    return str(resp.text)

@app.route("/files")
@jwt_required
def my_files():
    if(request.cookies.get(ACCESS_TOKEN) == None):
        abort(403)
    access_token = create_access_token(get_jwt_identity())
    headers = {
        "Authorization": "Bearer " + access_token
    }
    resp = requests.get(FILE_LIST_URL, verify=False, headers=headers)
    response = make_response(render_template("my_files.html", data = resp.json()))
    response.set_cookie("access_token_cookie", access_token, max_age = 180, secure = True, httponly = True)
    return response

@app.route("/addfile", methods=[GET, POST])
@jwt_required
def add_file():
    if request.method == GET:
        username = get_jwt_identity()
        access_token = create_access_token(username)
        response = make_response(render_template("add_file.html"))
        response.set_cookie("access_token_cookie", access_token, max_age = 180, secure = True, httponly = True)
        return response
    elif request.method == POST:
        username = get_jwt_identity()
        url = FILE_LIST_URL
        access_token = create_access_token(username)
        headers = {
            "Authorization": "Bearer " + access_token
        }
        files = {
            "my_file": (request.files["my_file"].filename, request.files["my_file"].read())
        }
        resp = requests.post(url, files=files, verify=False, headers = headers)
        response = make_response(redirect(url_for("my_files")))
        response.set_cookie(ACCESS_TOKEN, access_token, max_age = 180, secure = True, httponly = True)
        return response

@app.route("/delete_file/<int:id>")
@jwt_required
def delete_file(id):
    username = get_jwt_identity()
    access_token = create_access_token(username)
    url = FILE_URL + str(id)
    headers = {
        "Authorization": "Bearer " + access_token
    }
    resp = requests.delete(url, verify=False, headers = headers)
    if resp.json()["status"] == 200:
        response = make_response(redirect(url_for("my_files")))
        response.set_cookie(ACCESS_TOKEN, access_token, max_age = 180, secure = True, httponly = True)
        return response
    else:
        abort(404)

@app.errorhandler(403)
def page_forbidden(error):
    return render_template("errors/403.html", error = error)

@app.errorhandler(404)
def not_found(error):
    return render_template("errors/404.html", error = error)

@app.errorhandler(401)
def unauthorized(error):
    return render_template("errors/401.html", error = error)

@app.errorhandler(400)
def bad_request(error):
    return render_template("errors/400.html", error = error)