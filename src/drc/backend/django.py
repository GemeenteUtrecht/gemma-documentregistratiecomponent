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

    def create_document(self, enkelvoudiginformatieobject, bestand=None, link=None):
        from .models import DjangoStorage
        return DjangoStorage.objects.create(
            enkelvoudiginformatieobject=enkelvoudiginformatieobject,
            inhoud=bestand,
            link=link
        )

    def update_document(self, enkelvoudiginformatieobject, updated_values, bestand=None, link=None):
        if not hasattr(enkelvoudiginformatieobject, 'djangostorage'):
            raise AttributeError('Document has no djangostorage.')
        djangostorage = enkelvoudiginformatieobject.djangostorage
        djangostorage.inhoud = bestand
        djangostorage.link = link
        djangostorage.save()

    def remove_document(self, enkelvoudiginformatieobject):
        if not hasattr(enkelvoudiginformatieobject, 'djangostorage'):
            raise AttributeError('Document has no djangostorage.')

        enkelvoudiginformatieobject.djangostorage.delete()

    def connect_document_to_folder(self, enkelvoudiginformatieobject, zaak_url):
        # There are no folders created for django storage.
        pass
