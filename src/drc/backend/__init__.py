from django.conf import settings

from import_class import import_class, import_instance


class DRCStorageAdapter(object):
    backends = []

    def get_backends(self):
        from drc.plugins.models import StorageConfig
        config = StorageConfig.get_solo()

        config_backends = config.get_backends()

        if self.backends and len(self.backends) == len(config_backends):
            return self.backends

        for _temp_storage in config_backends:
            self.backends.append(import_instance(_temp_storage))

        return self.backends

    def get_folder(self, zaak_url):
        for backend in self.get_backends():
            backend.get_folder(zaak_url)

    def create_folder(self, zaak_url):
        for backend in self.get_backends():
            backend.create_folder(zaak_url)

    def rename_folder(self, old_zaak_url, new_zaak_url):
        for backend in self.get_backends():
            backend.rename_folder(old_zaak_url, new_zaak_url)

    def remove_folder(self, zaak_url):
        for backend in self.get_backends():
            backend.remove_folder(zaak_url)

    def get_document(self, enkelvoudiginformatieobject):
        for backend in self.get_backends():
            document = backend.get_document(enkelvoudiginformatieobject)
            TempDocument = import_class(settings.TEMP_DOCUMENT_CLASS)

            if not isinstance(document, TempDocument):
                raise ValueError('Returned document is not of the TempDocument type.')

            if document.url:
                return document
        return None

    def create_document(self, enkelvoudiginformatieobject, bestand=None, link=None):
        self._validate_contents(bestand, link)

        for backend in self.get_backends():
            backend.create_document(enkelvoudiginformatieobject, bestand=bestand, link=link)

    def update_document(self, enkelvoudiginformatieobject, updated_values, bestand=None, link=None):
        self._validate_contents(bestand, link)

        for backend in self.get_backends():
            backend.update_document(enkelvoudiginformatieobject, updated_values, bestand=bestand, link=link)

    def remove_document(self, enkelvoudiginformatieobject):
        for backend in self.get_backends():
            backend.remove_document(enkelvoudiginformatieobject)

    def connect_document_to_folder(self, enkelvoudiginformatieobject, zaak_url):
        for backend in self.get_backends():
            backend.connect_document_to_folder(enkelvoudiginformatieobject, zaak_url)

    def _validate_contents(self, bestand=None, link=None):
        if not bestand and not link:
            raise ValueError('No bestand and link provided. Either provide a bestand or link')


drc_storage_adapter = DRCStorageAdapter()
