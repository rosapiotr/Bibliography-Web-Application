class PublicationRequest:
    def __init__(self, request):
        self.author = request.json["author"]
        self.title = request.json["title"]
        self.year = request.json["year"]

    def __str__(self):
        return "author: {0}, title: {1}, year: {2}".format(self.author, self.title, self.year)