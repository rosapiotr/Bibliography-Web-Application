from flask import Flask
import redis
import json
import os

app = Flask(__name__)

FILE_ID_PREFIX = "file_"
FILE_COUNTER = "file_counter"
PATH_TO_FILE = "path"

class FileRepository:

    def __init__(self):
        self.db = redis.Redis(host = "redis", port = 6379, decode_responses = True)

    def save(self, file, username):
        if self.db.get(username + FILE_COUNTER) == None:
            self.db.set(username + FILE_COUNTER, 0)
        file_id = self.save_file(file, username)
        return file_id

    def save_file(self, file_to_save, login):
        if(len(file_to_save.filename) > 0):
            ctr = str(self.db.incr(login + FILE_COUNTER))
            file_id = FILE_ID_PREFIX + ctr
            new_filename = file_id + file_to_save.filename
            dir_path = "files/" + login
            try:
                os.mkdir(dir_path)
            except Exception as e:
                app.logger.debug(e.__doc__)
            path_to_file = dir_path + "/" + new_filename
            file_to_save.save(path_to_file)
            file_info = {
                "id": ctr,
                PATH_TO_FILE: path_to_file,
                "orginal": file_to_save.filename,
                "new": new_filename
            }
            json_info = json.dumps(file_info)

            self.db.hset(login, file_id, json_info)
            return ctr
        else:
            app.logger.debug("[WARN] Empty content of file")
            return -1

    def get_file_by_id(self, id, username):
        file_id = FILE_ID_PREFIX + str(id)
        if self.db.hexists(username, file_id):
            file_json = json.loads(self.db.hget(username, file_id))
            return file_json
        else:
            return "Nie ma pliku o takim id"

    def delete_file_by_id(self, id, username):
        file_id = FILE_ID_PREFIX + str(id)
        if self.db.hexists(username, file_id):
            file_path = json.loads(self.db.hget(username, file_id))["path"]
            self.db.hdel(username, file_id)
            os.remove(file_path)
            return {
                "status": 200,
                "message": "Successfully deleted file by ID"
            }
        else:
            return {
                "status": 404,
                "message": "Could not find file with given ID"
            }

    def get_all_files(self, username):
        app.logger.debug("Finding all files")
        try:
            n = int(self.db.get(username + FILE_COUNTER))
        except TypeError as e:
            n = 0
        app.logger.debug(username)
        app.logger.debug(n)
        files = []
        for i in range(1, n+1):
            file_id = FILE_ID_PREFIX + str(i)
            if not self.db.hexists(username, file_id):
                continue
            file_json = json.loads(self.db.hget(username, file_id))
            f_id = file_json["id"]
            f_org = file_json["orginal"]
            file_dict = { "id": f_id, "orginal": f_org }
            files.append(file_dict)
        app.logger.debug("Found {0} publications.".format(len(files)))
        return files