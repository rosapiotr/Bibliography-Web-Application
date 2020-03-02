from flask import Flask, request, send_file
from flask_restplus import Api, Resource, fields
import os
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from src.dto.request.publication_request import PublicationRequest
from src.service.publication_service import PublicationService
from src.service.file_service import FileService
from src.exception.exception import PublicationAlreadyExistsException
from flask_cors import CORS, cross_origin

SECRET_KEY = "PROJECT_SECRET"
TOKEN_EXPIRES_IN_SECONDS = 180

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, where JWT is the token"
    }
}

app = Flask(__name__)
api_app = Api(app = app, version = "0.1", title = "Project app API", description = "REST-full API for library", doc="/api",
    authorizations=authorizations, security='apikey')

app.secret_key = os.environ.get(SECRET_KEY)

publication_namespace = api_app.namespace("api/publication", description = "Publication API")
file_namespace = api_app.namespace("api/file", description = "File API")

app.config["JWT_SECRET_KEY"] = os.environ.get(SECRET_KEY)
app.config["JWT_TOKEN_LOCATION"] = ["cookies", "headers"]
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = TOKEN_EXPIRES_IN_SECONDS
app.config["JWT_COOKIE_CSRF_PROTECT"] = False
CORS(app)
jwt = JWTManager(app)

START = "start"
LIMIT = "limit"
PATH_TO_FILE = "path"

@publication_namespace.route("/<int:id>")
class Publication(Resource):
    def __init__(self, args):
        super().__init__(args)
        self.publication_service = PublicationService()

    @api_app.doc(responses = {200: "OK", 400: "Invalid argument"},
            params = {"id": "Specify publication Id"})
    @jwt_required
    def get(self, id):
        username = get_jwt_identity()
        try:
            publication = self.publication_service.get_publication(id, username)
            return publication.get_json(request.base_url)

        except TypeError as e:
            publication_namespace.abort(400, e.__doc__, status = "Could not find publication by id", statusCode = "400")

    @api_app.doc(responses = {200: "OK", 400: "Invalid argument"},
            params = {"id": "Specify publication Id to remove"})
    @jwt_required
    def delete(self, id):
        username = get_jwt_identity()
        try:
            deleted = self.publication_service.delete_publication(id, username)
            if deleted.status == 200:
                return deleted.get_json(request.base_url)
        except TypeError as e:
            publication_namespace.abort(400, e.__doc__, status = "Could not delete by id", statusCode = "400")

        except KeyError as e:
            publication_namespace.abort(400, e.__doc__, status = "Could not delete by id", statusCode = "400")

    new_put_model = api_app.model("Put model",
            {
                "file_id": fields.Integer(required = True, description = "File ID", help = "File ID cannot be null", example = "2"),
            })

    @api_app.expect(new_put_model)
    @jwt_required
    def put(self, id):
        username = get_jwt_identity()
        response = self.publication_service.update_publication(id, request, username)
        return response

@publication_namespace.route("/list")
class PublicationList(Resource):

    def __init__(self, args):
        super().__init__(args)
        self.publication_service = PublicationService()

    new_publication_model = api_app.model("Publication model",
            {
                "title": fields.String(required = True, description = "Publication title", help = "Title cannot be null", example = "Bieguni"),
                "year": fields.Integer(required = True, description = "Year of publication", help = "Year cannot be null", example = "2007"),
                "author": fields.Integer(required = True, description = "Author's Name", help = "Author's Name cannot be null", example = "Olga Tokarczuk")
            })

    @api_app.param(START, "The data will be returned from this position.")
    @api_app.param(LIMIT, "The max size of returned data.")
    @api_app.doc(responses = {200: "OK"})
    @jwt_required
    def get(self):
        username = get_jwt_identity()
        start = self.parse_request_arg_or_zero(request, START, "0")
        start = max(1, start)
        limit = self.parse_request_arg_or_zero(request, LIMIT, "50")

        paginated_publication_response = self.publication_service.get_paginated_publications_response(start, limit, username)

        return paginated_publication_response.get_json(request.base_url)

    def parse_request_arg_or_zero(self, request, param, default_value):
        val = request.args.get(param, default_value)
        val = int(val) if val.isdigit() else 0
        return val

    @api_app.expect(new_publication_model)
    @jwt_required
    def post(self):
        try:
            username = get_jwt_identity()
            publication_req = PublicationRequest(request)
            saved_publication_id = self.publication_service.add_publication(publication_req, username)

            result = {"status_code": 200, "message": "Added new publication", "saved_publication_id": saved_publication_id}

            return result

        except KeyError as e:
            publication_namespace.abort(400, e.__doc__, status = "Could not save new publication", statusCode = "400")

        except TypeError as e:
            publication_namespace.abort(400, e.__doc__, status = "Could not save new publication", statusCode = "400")

        except PublicationAlreadyExistsException as e:
            publication_namespace.abort(409, e.__doc__, status = "Could not save new publication. Already exists", statusCode = "409")

@file_namespace.route("/list")
class FileList(Resource):

    def __init__(self, args):
        super().__init__(args)
        self.file_service = FileService()

    @jwt_required
    def post(self):
        username = get_jwt_identity()
        f = request.files["my_file"] 
        file_id = self.file_service.add_file(f, username)
        if file_id != -1:
            result = {"status_code": 200, "message": "Added new file", "saved_file_id": file_id}
            return result
        else:
            publication_namespace.abort(400, status = "Could not save new file", statusCode = "400")
        return f.filename

    @jwt_required
    def get(self):
        username = get_jwt_identity()
        files = self.file_service.get_all_files(username)
        return files

@file_namespace.route("/<int:id>")
class My_File(Resource):
    
    def __init__(self, args):
        super().__init__(args)
        self.file_service = FileService()

    @jwt_required
    def get(self, id):
        username = get_jwt_identity()
        try:
            file_json = self.file_service.get_file(id, username)
            full_name = file_json[PATH_TO_FILE]
            orginal = file_json["orginal"]
            if (full_name != None):
                return send_file(full_name, attachment_filename = orginal, as_attachment=True)
            return "Moze byc None?"
        except Exception as e:
            return {
                "status": 404,
                "message": "Could not find file with given ID"
            }
            return e.__doc__

        except TypeError as e:
            publication_namespace.abort(400, e.__doc__, status = "Could not find publication by id", statusCode = "400")

    @jwt_required
    def delete(self, id):
        username = get_jwt_identity()
        try:
            resp = self.file_service.delete_file(id, username)
            return resp
        except Exception as e:
            return e.__doc__
