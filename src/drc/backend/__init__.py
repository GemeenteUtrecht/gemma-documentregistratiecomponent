from uuid import uuid4

from django.conf import settings
from django.utils import timezone
from django.utils.module_loading import import_string


class DRCStorageAdapter:
    backends = []

    def __init__(self):
        imported_class = import_string('drc.backend.django.DjangoDRCStorageBackend')

        if settings.CMIS_ENABLED:
            imported_class = import_string('drc_cmis.backend.CMISDRCStorageBackend')

        self.backend = imported_class()

    # Documenten
    def creeer_enkelvoudiginformatieobject(self, gevalideerde_data):
        inhoud = gevalideerde_data.pop('inhoud')

        # * Add a default identificatie (uuid4) is no identification is passed
        if not gevalideerde_data.get('identificatie'):
            gevalideerde_data['identificatie'] = uuid4()

        data = self.backend.create_document(data=gevalideerde_data.copy(), content=inhoud)
        return data

    def lees_enkelvoudiginformatieobjecten(self, filters):
        return self.backend.get_documents(filters=filters)

    def lees_enkelvoudiginformatieobject(self, identificatie):
        return self.backend.get_document(identification=identificatie)

    def update_enkenvoudiginformatieobject(self, identificatie, gevalideerde_data):
        inhoud = gevalideerde_data.pop('inhoud', None)
        return self.backend.update_document(
            identification=identificatie,
            data=gevalideerde_data.copy(),
            content=inhoud
        )

    def verwijder_enkelvoudiginformatieobject(self, identificatie):
        return self.backend.delete_document(identification=identificatie)

    # Connecties
    def creeer_objectinformatieobject(self, gevalideerde_data):
        gevalideerde_data['registratiedatum'] = timezone.now()
        return self.backend.create_document_case_connection(data=gevalideerde_data.copy())

    def lees_objectinformatieobjecten(self):
        return self.backend.get_document_case_connections()

    def lees_objectinformatieobject(self, identificatie):
        return self.backend.get_document_case_connection(identification=identificatie)

    def update_objectinformatieobject(self, identificatie, gevalideerde_data):
        return self.backend.update_document_case_connection(identification=identificatie, data=gevalideerde_data.copy())

    def verwijder_objectinformatieobject(self, identificatie):
        return self.backend.delete_document_case_connection(identification=identificatie)


drc_storage_adapter = DRCStorageAdapter()
