from django.conf import settings

from drc.backend.abstract import BaseDRCStorageBackend
from .client import default_client
from .models import DRCCMISConnection


class CMISDRCStorageBackend(BaseDRCStorageBackend):
    """
    This is the backend that is used to store the documents in a CMIS compatible backend.
    """
    def get_folder(self, zaak_url):
        # Folders will not be supported for now
        pass

    def create_folder(self, zaak_url):
        # Folders will not be supported for now
        pass

    def rename_folder(self, old_zaak_url, new_zaak_url):
        # Folders will not be supported for now
        pass

    def remove_folder(self, zaak_url):
        # Folders will not be supported for now
        pass

    def get_document(self, enkelvoudiginformatieobject):
        raise NotImplementedError()

    def create_document(self, enkelvoudiginformatieobject):
        connection = DRCCMISConnection.objects.create(enkelvoudiginformatieobject=enkelvoudiginformatieobject, cmis_object_id='')

        cmis_doc = default_client.maak_zaakdocument_met_inhoud(
            connection=connection,
            zaak_url=None,
            filename=None,
            sender=settings.CMIS_SENDER_PROPERTY,
            stream=enkelvoudiginformatieobject.inhoud
        )
        connection.cmis_object_id = cmis_doc.getObjectId().rsplit(';')[0]
        connection.save()

    def update_document(self, enkelvoudiginformatieobject):
        raise NotImplementedError()

    def remove_document(self, enkelvoudiginformatieobject):
        raise NotImplementedError()

    def move_document(self, enkelvoudiginformatieobject):
        raise NotImplementedError()
