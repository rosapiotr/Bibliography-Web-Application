import json

class Publication:
    def __init__(self, id, author, title, year, files=[]):
        self.id = id
        self.author = author
        self.title = title
        self.year = year
        self.files = files

    @classmethod
    def from_json(cls, data):
        return cls(**data)