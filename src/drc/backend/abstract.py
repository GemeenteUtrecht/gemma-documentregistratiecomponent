from .data import EnkelvoudigInformatieObject
from .exceptions import BackendException


class BaseDRCStorageBackend:
    """
    This is the base Backend storage for the DRC where it should all be based on.
    """
    def __init__(self):
        self.exception_class = BackendException
        self.dataclass = EnkelvoudigInformatieObject

    # DOCUMENTS ====================================================================================
    # CREATE
    def create_document(self, validated_data, inhoud):
        raise NotImplementedError()

    # READ
    def get_documents(self, filters):
        raise NotImplementedError()

    def get_document(self, uuid):
        raise NotImplementedError()

    # UPDATE
    def update_document(self, validated_data, identificatie, inhoud):
        raise NotImplementedError()

    # DELETE
    def delete_document(self, uuid):
        raise NotImplementedError()

    # CONNECTIONS ==================================================================================
    # CREATE
    def create_case_link(self, validated_data):
        raise NotImplementedError()

    # READ
    def get_document_cases(self):
        """
        Get all documents that have a case url.
        """
        raise NotImplementedError()

    # UPDATE
    # TODO

    # DELETE
    # TODO
