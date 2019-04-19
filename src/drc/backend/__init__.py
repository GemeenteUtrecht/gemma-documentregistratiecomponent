from importlib import import_module

from django.conf import settings

DRC_STORAGE_BACKENDS = getattr(settings, 'DRC_STORAGE_BACKENDS', [])


class DRCStorageAdapter(object):
    def __init__(self):
        self.backends = self._get_backends()

    def _get_backends(self):
        assert isinstance(DRC_STORAGE_BACKENDS, list), "DRC_STORAGE_BACKENDS is not a list of backends"

        backends = []
        if settings.DRC_BUILDIN_BACKEND:
            from .django import DjangoDRCStorageBackend
            backends.append(DjangoDRCStorageBackend())

        for _temp_storage in DRC_STORAGE_BACKENDS:
            package, klass = _temp_storage.rsplit('.', 1)
            module = import_module(package)
            backend = getattr(module, klass)
            backends.append(backend())

        return backends

    def get_folder(self, zaak_url):
        for backend in self.backends:
            backend.get_folder(zaak_url)

    def create_folder(self, zaak_url):
        for backend in self.backends:
            backend.create_folder(zaak_url)

    def rename_folder(self, old_zaak_url, new_zaak_url):
        for backend in self.backends:
            backend.rename_folder(old_zaak_url, new_zaak_url)

    def remove_folder(self, zaak_url):
        for backend in self.backends:
            backend.remove_folder(zaak_url)

    def get_document(self, enkelvoudiginformatieobject):
        return self.backends[0].get_document(enkelvoudiginformatieobject)

    def create_document(self, enkelvoudiginformatieobject):
        for backend in self.backends:
            backend.create_document(enkelvoudiginformatieobject)

    def update_document(self, enkelvoudiginformatieobject, updated_values):
        for backend in self.backends:
            backend.update_document(enkelvoudiginformatieobject, updated_values)

    def remove_document(self, enkelvoudiginformatieobject):
        for backend in self.backends:
            backend.remove_document(enkelvoudiginformatieobject)

    def move_document(self, enkelvoudiginformatieobject, zaak_url):
        for backend in self.backends:
            backend.move_document(enkelvoudiginformatieobject, zaak_url)


drc_storage_adapter = DRCStorageAdapter()
