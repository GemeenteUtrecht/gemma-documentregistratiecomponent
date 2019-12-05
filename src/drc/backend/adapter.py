import logging
from uuid import uuid4

from django.conf import settings
from django.utils import timezone
from django.utils.module_loading import import_string

logger = logging.getLogger(__name__)


class DRCStorageAdapter:
    backends = []

    def __init__(self):
        imported_class = import_string('drc.backend.django.DjangoDRCStorageBackend')

        if settings.CMIS_ENABLED:
            imported_class = import_string('drc_cmis.backend.CMISDRCStorageBackend')

        self.backend = imported_class

    # Documenten
    def creeer_enkelvoudiginformatieobject(self, gevalideerde_data):
        inhoud = gevalideerde_data.pop('inhoud')

        # * Add a default identificatie (uuid4) is no identification is passed
        if not gevalideerde_data.get('identificatie'):
            gevalideerde_data['identificatie'] = uuid4()

        data = self.backend().create_document(data=gevalideerde_data.copy(), content=inhoud)
        return data

    def lees_enkelvoudiginformatieobjecten(self, page, page_size, filters):
        if filters:
            filters = {key: value for key, value in filters.items() if value is not None}
        return self.backend().get_documents(page=page, page_size=page_size, filters=filters)

    def lees_enkelvoudiginformatieobject(self, uuid, versie=None, filters=None):
        if filters:
            filters = {key: value for key, value in filters.items() if value is not None}
        return self.backend().get_document(uuid=uuid, version=versie, filters=filters)

    def lees_enkelvoudiginformatieobject_inhoud(self, uuid):
        return self.backend().get_document_content(uuid=uuid)

    def update_enkenvoudiginformatieobject(self, uuid, lock, gevalideerde_data):
        inhoud = gevalideerde_data.pop('inhoud', None)
        return self.backend().update_document(
            uuid=uuid,
            lock=lock,
            data=gevalideerde_data.copy(),
            content=inhoud
        )

    def verwijder_enkelvoudiginformatieobject(self, uuid):
        return self.backend().delete_document(uuid=uuid)

    def lock_enkelvoudiginformatieobject(self, uuid):
        return self.backend().lock_document(uuid=uuid)

    def unlock_enkelvoudiginformatieobject(self, uuid, lock, force=False):
        return self.backend().unlock_document(uuid=uuid, lock=lock, force=force)

    # Connecties
    def creeer_objectinformatieobject(self, gevalideerde_data):
        gevalideerde_data['registratiedatum'] = timezone.now()
        return self.backend().create_document_case_connection(data=gevalideerde_data.copy())

    def lees_objectinformatieobjecten(self, filters=None):
        if filters:
            filters = {key: value for key, value in filters.items() if value is not None}
        return self.backend().get_document_case_connections(filters=filters)

    def lees_objectinformatieobject(self, uuid):
        return self.backend().get_document_case_connection(uuid=uuid)

    def update_objectinformatieobject(self, uuid, gevalideerde_data):
        return self.backend().update_document_case_connection(uuid=uuid, data=gevalideerde_data.copy())

    def verwijder_objectinformatieobject(self, uuid):
        return self.backend().delete_document_case_connection(uuid=uuid)


drc_storage_adapter = DRCStorageAdapter()
