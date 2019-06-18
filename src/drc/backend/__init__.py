from uuid import uuid4

from django.conf import settings

from import_class import import_class, import_instance


class DRCStorageAdapter:
    backends = []

    def __init__(self):
        self.backend = import_instance('drc.backend.django.DjangoDRCStorageBackend')

        if settings.CMIS_ENABLED:
            self.backend = import_instance('drc_cmis.backend.CMISDRCStorageBackend')

    def create_enkelvoudiginformatieobject(self, validated_data):
        inhoud = validated_data.pop('inhoud')

        # Add a default identificatie (uuid4) is no identification is passed
        if not validated_data.get('identificatie'):
            validated_data['identificatie'] = uuid4()

        data = self.backend.create_document(validated_data.copy(), inhoud)
        return data

    def get_documents(self, filters):
        print(filters)
        return self.backend.get_documents(filters)

    def update_enkenvoudiginformatieobject(self, validated_data, identificatie):
        inhoud = validated_data.pop('inhoud')
        return self.backend.update_document(validated_data.copy(), identificatie, inhoud)

    def get_document(self, uuid):
        return self.backend.get_document(uuid)

    def get_document_cases(self):
        return self.backend.get_document_cases()

    def create_objectinformatieobject(self, validated_data):
        return self.backend.create_case_link(validated_data.copy())

    def delete_document(self, uuid):
        return self.backend.delete_document(uuid)

    # def get_folder(self, zaak_url):
    #     for backend in self.get_backends():
    #         backend.get_folder(zaak_url)

    # def create_folder(self, zaak_url):
    #     for backend in self.get_backends():
    #         backend.create_folder(zaak_url)

    # def rename_folder(self, old_zaak_url, new_zaak_url):
    #     for backend in self.get_backends():
    #         backend.rename_folder(old_zaak_url, new_zaak_url)

    # def remove_folder(self, zaak_url):
    #     for backend in self.get_backends():
    #         backend.remove_folder(zaak_url)

    # def get_document(self, enkelvoudiginformatieobject):
    #     for backend in self.get_backends():
    #         document = backend.get_document(enkelvoudiginformatieobject)
    #         TempDocument = import_class(settings.TEMP_DOCUMENT_CLASS)

    #         if not isinstance(document, TempDocument):
    #             raise ValueError('Returned document is not of the TempDocument type.')

    #         if document.url:
    #             return document
    #     return None

    # def remove_document(self, enkelvoudiginformatieobject):
    #     for backend in self.get_backends():
    #         backend.remove_document(enkelvoudiginformatieobject)

    # def connect_document_to_folder(self, enkelvoudiginformatieobject, zaak_url):
    #     for backend in self.get_backends():
    #         backend.connect_document_to_folder(enkelvoudiginformatieobject, zaak_url)

    # def _validate_contents(self, bestand=None, link=None):
    #     if not bestand and not link:
    #         raise ValueError('No bestand and link provided. Either provide a bestand or link')


drc_storage_adapter = DRCStorageAdapter()
