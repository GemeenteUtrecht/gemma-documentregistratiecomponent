class BaseDRCStorageBackend:
    """
    This is the base Backend storage for the DRC where it should all be based on.
    """
    def get_folder(self, zaak_url):
        raise NotImplementedError()

    def create_folder(self, zaak_url):
        raise NotImplementedError()

    def rename_folder(self, old_zaak_url, new_zaak_url):
        raise NotImplementedError()

    def remove_folder(self, zaak_url):
        raise NotImplementedError()

    def get_document(self, enkelvoudiginformatieobject):
        raise NotImplementedError()

    def create_document(self, enkelvoudiginformatieobject):
        raise NotImplementedError()

    def update_document(self, enkelvoudiginformatieobject, updated_values):
        raise NotImplementedError()

    def remove_document(self, enkelvoudiginformatieobject):
        raise NotImplementedError()

    def move_document(self, enkelvoudiginformatieobject, zaak_url):
        raise NotImplementedError()
