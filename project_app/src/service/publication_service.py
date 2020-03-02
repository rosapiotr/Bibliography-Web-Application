from flask import Flask
from src.service.repositories.publication_repository import PublicationRepository
from src.dto.response.paginated_publication_response import PaginatedPublicationResponse
from src.dto.response.publication_response import PublicationResponse
from src.dto.response.delete_response import DeleteResponse

app = Flask(__name__)

class PublicationService:

    def __init__(self):
        self.publication_repo = PublicationRepository()

    def get_publication(self, publication_id, username):
        app.logger.debug("Getting publication...")
        publication = self.publication_repo.get_publication_by_id(publication_id, username)
        publication_response = PublicationResponse(publication["publication"], publication["previous"], publication["next"])
        app.logger.debug("Got publication.")
        return publication_response

    def delete_publication(self, publication_id, username):
        app.logger.debug("Deleting publication...")
        response = self.publication_repo.delete_publication_by_id(publication_id, username)
        delete_response = DeleteResponse(response["status"], response["message"], response["previous"], response["next"])
        app.logger.debug("Deleted publication.")
        return delete_response

    def update_publication(self, publication_id, file_request, username):
        app.logger.debug("Updating publication...")
        response = self.publication_repo.update_publication(publication_id, file_request, username)
        app.logger.debug("Updated publication.")
        return response

    def add_publication(self, publication_req, username):
        app.logger.debug("Adding publication...")
        publication_id = self.publication_repo.save(publication_req, username)
        app.logger.debug("Added publication (id: {0})".format(publication_id))
        return publication_id

    def get_paginated_publications_response(self, start, limit, username):
        app.logger.debug("Getting paginated publications (start: {0}, limit: {1})".format(start, limit))
        n_of_publications = self.publication_repo.count_all(username)

        publications = self.publication_repo.find_n_publications(start, limit, username)

        publications_response = PaginatedPublicationResponse(publications, start, limit, n_of_publications)

        app.logger.debug("Got paginated publications (start: {0}, limit: {1}, count: {2}, current_size: {3})".format(start, limit, n_of_publications, len(publications)))
        return publications_response