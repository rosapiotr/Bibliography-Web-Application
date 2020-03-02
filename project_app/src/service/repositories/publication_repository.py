from flask import Flask
import redis
import json

from ...service.entity.publication import Publication
from ...exception.exception import PublicationAlreadyExistsException

app = Flask(__name__)

PUBLICATION_ID_PREFIX = "publication_"
FILE_COUNTER = "file_counter"
PUBLICATION_COUNTER = "publication_counter"

class PublicationRepository:

    def __init__(self):
        self.db = redis.Redis(host = "redis", port = 6379, decode_responses = True)

    def save(self, publication_req, username):
        if self.db.get(username + PUBLICATION_COUNTER) == None:
            self.db.set(username + PUBLICATION_COUNTER, 0)
        app.logger.debug("Saving new publication: {0}.".format(publication_req))
        publication = self.find_publication_by_title(publication_req.title, username)

        if publication != None:
            raise PublicationAlreadyExistsException("Publication title \"{0}\" already exist.".format(publication_req.title))

        publication = Publication(self.db.incr(username + PUBLICATION_COUNTER), publication_req.author, publication_req.title, publication_req.year)

        publication_id = PUBLICATION_ID_PREFIX + str(publication.id)
        publication_json = json.dumps(publication.__dict__)

        self.db.hset(username, publication_id, publication_json)

        app.logger.debug("Saved new publication: (id: {0}).".format(publication.id))
        return publication.id

    def update_publication(self, id, file_request, username):
        if self.db.get(username + PUBLICATION_COUNTER) == None:
            self.db.set(username + PUBLICATION_COUNTER, 0)
        n = int(self.db.get(username + PUBLICATION_COUNTER))
        publication_id = PUBLICATION_ID_PREFIX + str(id)
        f_id = file_request.json["file_id"]

        if self.db.hexists(username, publication_id):
            publication_json = self.db.hget(username, publication_id)
            publication = Publication.from_json(json.loads(publication_json))
            if not self.db.hexists(username, "file_" + str(f_id)):
                if len(publication.files) > 0:
                    for f in publication.files:
                        if f["file_id"] == f_id:
                            publication.files.remove(f)
                            publication_j = json.dumps(publication.__dict__)
                            self.db.hset(username, publication_id, publication_j)
                            return {
                                "status": 204,
                                "message": "File with given id does not exist"
                            }
                return {
                    "status": 404,
                    "message": "File with given id does not exist"
                }
            file_json = json.loads(self.db.hget(username, "file_" + str(f_id)))
            f_name = file_json["orginal"]
            url = "https://localhost:8081/api/file/" + str(f_id)
            if len(publication.files) > 0:
                for f in publication.files:
                    if f["file_id"] == f_id:
                        publication.files.remove(f)
                        publication_j = json.dumps(publication.__dict__)
                        self.db.hset(username, publication_id, publication_j)
                        return {
                            "status": 200,
                            "message": "Sucesfully unattached file"
                        }
            publication.files.append({ "file_id": f_id, "file_url": url, "filename": f_name })
            publication_j = json.dumps(publication.__dict__)
            self.db.hset(username, publication_id, publication_j)
            return {
                "status": 200,
                "message": "Successfully updated publication by id"
            }
        else:
            return {
                    "status": 404,
                    "message": "Publication with given id does not exist"
            }

    def get_prev_and_next(self, id, n, username):
        prev_pub_id = ""
        next_pub_id = ""

        for prev in range(1, id):
            previous_publication_id = PUBLICATION_ID_PREFIX + str(prev)
            if not self.db.hexists(username, previous_publication_id):
                continue
            prev_pub_id = prev

        for nex in range(id + 1, n + 1):
            next_publication_id = PUBLICATION_ID_PREFIX + str(nex)
            if not self.db.hexists(username, next_publication_id):
                continue
            next_pub_id = nex
            break
        return (prev_pub_id, next_pub_id)

    def get_publication_by_id(self, id, username):
        n = int(self.db.get(username + PUBLICATION_COUNTER))
        publication_id = PUBLICATION_ID_PREFIX + str(id)
        
        if self.db.hget(username, publication_id):
            publication_json = self.db.hget(username, publication_id)
            publication = Publication.from_json(json.loads(publication_json))

            prev_pub_id, next_pub_id = self.get_prev_and_next(id, n, username)

            publications = {
                "previous": prev_pub_id,
                "publication": publication,
                "next": next_pub_id
            }

            return publications
        else:
            return -1

    def delete_publication_by_id(self, id, username):
        n = int(self.db.get(username + PUBLICATION_COUNTER))
        publication_id = PUBLICATION_ID_PREFIX + str(id)

        if self.db.hget(username, publication_id):
            self.db.hdel(username, publication_id)
            prev_pub_id, next_pub_id = self.get_prev_and_next(id, n, username)
            return {
                "previous": prev_pub_id,
                "status": 200,
                "message": "Successfully deleted publication by id",
                "next": next_pub_id
            }
        else:
            return {
                "status": 404
            }

    def find_publication_by_title(self, title, username):
        n = int(self.db.get(username + PUBLICATION_COUNTER))

        for i in range(1, n + 1):
            publication_id = PUBLICATION_ID_PREFIX + str(i)

            if not self.db.hexists(username, publication_id):
                continue

            publication_json = self.db.hget(username, publication_id)
            publication = Publication.from_json(json.loads(publication_json))

            if publication.title == title:
                return publication

        return None

    def count_all(self, username):
        app.logger.debug("Starting counting all publications")
        try:
            n = int(self.db.get(username + PUBLICATION_COUNTER))
        except TypeError as e:
            n = 0

        n_of_publications = 0

        for i in range(1, n + 1):
            publication_id = PUBLICATION_ID_PREFIX + str(i)

            if self.db.hexists(username, publication_id):
                n_of_publications += 1

        app.logger.debug("Counted all publications (n: {0})".format(n_of_publications))
        return n_of_publications

    def find_n_publications(self, start, limit, username):
        app.logger.debug("Finding n of publications (start: {0}, limit: {1}".format(start, limit))
        try:
            n = int(self.db.get(username + PUBLICATION_COUNTER))
        except TypeError as e:
            n = 0

        publications = []
        counter = 1

        for i in range(1, n + 1):
            publication_id = PUBLICATION_ID_PREFIX + str(i)

            if not self.db.hexists(username, publication_id):
                continue

            if counter < start:
                counter += 1
                continue

            publication_json = self.db.hget(username, publication_id)
            publication = Publication.from_json(json.loads(publication_json))
            publications.append(publication)

            if len(publications) >= limit:
                break

        app.logger.debug("Found {0} publications.".format(len(publications)))
        return publications