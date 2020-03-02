function deletePublication() {
    publication_id = window.location.href.substring(window.location.href.lastIndexOf('/') + 1);
    window.location.href = "https://localhost:8082/delete_publication/" + publication_id
}