from .exceptions import BackendException


class BaseDRCStorageBackend:
    """
    This is the base Backend storage for the DRC where it should all be based on.
    """
    def __init__(self):
        self.exception_class = BackendException

    def create_document(self, validated_data, inhoud):
        raise NotImplementedError()

    def get_documents(self):
        raise NotImplementedError()

    def update_enkelvoudiginformatieobject(self, validated_data, identificatie, inhoud):
        raise NotImplementedError()

    def get_document(self, uuid):
        raise NotImplementedError()

    def get_document_cases(self):
        """
        Get all documents that have a case url.
        """
        raise NotImplementedError()

    def create_case_link(self, validated_data):
        raise NotImplementedError()
