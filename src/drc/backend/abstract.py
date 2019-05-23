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
