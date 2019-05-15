from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from import_class import import_class


class DjangoDRCStorageBackend(import_class(settings.ABSTRACT_BASE_CLASS)):
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
        TempDocument = import_class(settings.TEMP_DOCUMENT_CLASS)
        try:
            storage = enkelvoudiginformatieobject.djangostorage
        except ObjectDoesNotExist:
            return TempDocument()
        else:
            return TempDocument(
                url=storage.inhoud.url,
                auteur=enkelvoudiginformatieobject.auteur,
                bestandsnaam=enkelvoudiginformatieobject.bestandsnaam,
                creatiedatum=enkelvoudiginformatieobject.creatiedatum,
                vertrouwelijkheidaanduiding=enkelvoudiginformatieobject.vertrouwelijkheidaanduiding,
                taal=enkelvoudiginformatieobject.taal,
            )

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
