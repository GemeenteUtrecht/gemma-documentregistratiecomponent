from .data import (
    EnkelvoudigInformatieObject, ObjectInformatieObject, PaginationObject
)
from .exceptions import BackendException


class BaseDRCStorageBackend:
    """
    This is the base Backend storage for the DRC where it should all be based on.
    """
    def __init__(self):
        self.exception_class = BackendException
        self.eio_dataclass = EnkelvoudigInformatieObject
        self.oio_dataclass = ObjectInformatieObject
        self.pagination_dataclass = PaginationObject

    def create_document(self, data, content):
        """
        Creates a document.

        Args:
            data (dict): A dict containing the values returned from the serializer.
            content (BytesStream): The content of the document.

        Returns:
            dataclass: An enkelvoudig informatieobject dataclass.

        Raises:
            NotImpletedError: This is not implemented yet.

        """
        raise NotImplementedError()

    def get_documents(self, page, page_size, filters=None):
        """
        Fetch all documents.

        Args:
            filters (dict or None): A dict with the filters that need to be applied.

        Returns:
            dataclass: A list of enkelvoudig informatieobject dataclass.

        Raises:
            NotImpletedError: This is not implemented yet.

        """
        raise NotImplementedError()

    def get_document(self, uuid, version=None, filters=None):
        """
        Get a single a document.

        Args:
            uuid (str): The cmis object id (only the uuid part)

        Returns:
            dataclass: An enkelvoudig informatieobject dataclass.

        Raises:
            NotImpletedError: This is not implemented yet.

        """
        raise NotImplementedError()

    def get_document_content(self, uuid):
        """
        Get a single a document.

        Args:
            uuid (str): The cmis object id (only the uuid part)

        Returns:
            dataclass: An enkelvoudig informatieobject dataclass.

        Raises:
            NotImpletedError: This is not implemented yet.

        """
        raise NotImplementedError()

    def update_document(self, uuid, lock, data, content=None):
        """
        Update a document.

        Args:
            uuid (str): The uuid from the document.
            data (dict): A dict with the fields that need to be updated.
            content (BytesStream): The content of the document.

        Returns:
            dataclass: An enkelvoudig informatieobject dataclass.

        Raises:
            NotImpletedError: This is not implemented yet.

        """
        raise NotImplementedError()

    def delete_document(self, uuid):
        """
        Deletes a document.

        Args:
            uuid (str): The uuid of the document.

        Returns:
            dataclass: An enkelvoudig informatieobject dataclass.

        Raises:
            NotImpletedError: This is not implemented yet.

        """
        raise NotImplementedError()

    def lock_document(self, uuid):
        raise NotImplementedError()

    def unlock_document(self, uuid, lock, force=False):
        raise NotImplementedError()

    def create_document_case_connection(self, data):
        """
        Creates a connection between a document and a case folder.

        Args:
            data (dict): A dict containing the values returned from the serializer.

        Returns:
            dataclass: An object informatieobject dataclass.

        Raises:
            NotImpletedError: This is not implemented yet.

        """
        raise NotImplementedError()

    def get_document_case_connections(self, filters=None):
        """
        Get all documents that have a case url.

        Returns:
            dataclass: A list of object informatieobject dataclass.

        Raises:
            NotImpletedError: This is not implemented yet.

        """
        raise NotImplementedError()

    def get_document_case_connection(self, uuid):
        """
        Get a single document that has a case url.

        Args:
            uuid (str): the CMIS id from the connected document.

        Returns:
            dataclass: A object informatieobject dataclass.

        Raises:
            NotImpletedError: This is not implemented yet.

        """
        raise NotImplementedError()

    def update_document_case_connection(self, uuid, data):
        """
        Updates a document/case connection.

        Args:
            uuid (str): The CMIS id of the document.
            data (dict): The data that needs to be updated.

        Returns:
            dataclass: A object informatieobject dataclass.

        Raises:
            NotImpletedError: This is not implemented yet.

        """
        raise NotImplementedError()

    def delete_document_case_connection(self, uuid):
        """
        Remove the connection between a document and a case.

        Args:
            uuid (str): The CMIS id of the document.

        Returns:
            dataclass: A object informatieobject dataclass.

        Raises:
            NotImpletedError: This is not implemented yet.

        """
        raise NotImplementedError()
