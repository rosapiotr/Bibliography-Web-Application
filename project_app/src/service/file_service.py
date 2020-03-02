from flask import Flask
from src.service.repositories.file_repository import FileRepository

app = Flask(__name__)

class FileService:

    def __init__(self):
        self.file_repo = FileRepository()

    def get_file(self, file_id, username):
        app.logger.debug("Getting file...")
        file_details = self.file_repo.get_file_by_id(file_id, username)
        app.logger.debug("Got file. ID: {0}".format(file_id))
        return file_details

    def delete_file(self, file_id, username):
        app.logger.debug("Deleting file...")
        resp = self.file_repo.delete_file_by_id(file_id, username)
        app.logger.debug("Deleted file with ID: {0}".format(file_id))
        return resp

    def get_all_files(self, username):
        app.logger.debug("Getting files...")
        files = self.file_repo.get_all_files(username)
        app.logger.debug("Got list of files")
        return files

    def add_file(self, file, username):
        app.logger.debug("Adding file...")
        file_id = self.file_repo.save(file, username)
        app.logger.debug("Added file (id: {0})".format(file_id))
        return file_id