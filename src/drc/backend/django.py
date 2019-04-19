from django.conf import settings

from drc.backend.abstract import BaseDRCStorageBackend


class DjangoDRCStorageBackend(BaseDRCStorageBackend):
    """
    This is the backend that is used to store the documents in a CMIS compatible backend.
    """
    def get_folder(self, zaak_url):
        # There are no folders created for django storage.
        pass

    def create_folder(self, zaak_url):
        # There are no folders created for django storage.
        pass

    def rename_folder(self, old_zaak_url, new_zaak_url):
        # There are no folders created for django storage.
        pass

    def remove_folder(self, zaak_url):
        # There are no folders created for django storage.
        pass

    def get_document(self, enkelvoudiginformatieobject):
        return enkelvoudiginformatieobject.inhoud.url

    def create_document(self, enkelvoudiginformatieobject):
        enkelvoudiginformatieobject.save(backend_save=True)

    def update_document(self, enkelvoudiginformatieobject, updated_values):
        enkelvoudiginformatieobject.save(backend_save=True)

    def remove_document(self, enkelvoudiginformatieobject):
        # This should be default behaviour from django.
        pass

    def move_document(self, enkelvoudiginformatieobject, zaak_url):
        # There are no folders created for django storage.
        pass
