from flask import jsonify
import json

class PublicationResponse:
    def __init__(self, publication, previous_id, next_id):
        self.publication = publication
        self.previous_id = previous_id
        self.next_id = next_id

    def get_json(self, url):
        if url.endswith("/"):
            url = url.rsplit("/", 2)[0]
        else:
            url = url.rsplit("/", 1)[0]

        if self.previous_id == "":
            previous_url = ""
        else:
            previous_url = "{0}/{1}".format(url, self.previous_id)

        if self.next_id == "":
            next_url = ""
        else:
            next_url = "{0}/{1}".format(url, self.next_id)

        return {
                "publication": self.publication.__dict__,
                "previous": previous_url,
                "next": next_url
                }