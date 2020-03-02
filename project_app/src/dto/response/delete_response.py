from flask import jsonify
import json

class DeleteResponse:
    def __init__(self, status, message, previous_id, next_id):
        self.status = status
        self.previous_id = previous_id
        self.next_id = next_id
        self.message = message

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
                "status": self.status,
                "message": self.message,
                "previous": previous_url,
                "next": next_url
                }