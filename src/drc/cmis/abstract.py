from collections import OrderedDict
from io import BytesIO

from cmislib.atompub.binding import AtomPubDocument


class DRCClient:
    """
    Abstract base class for DRC interaction.
    """
    TEMP_FOLDER_NAME = '_temp'
    TRASH_FOLDER = 'Unfiled'

    def creeer_zaakfolder(self, zaak_url):
        raise NotImplementedError

    def maak_zaakdocument(self, document, zaak_url=None, filename=None, sender=None):
        raise NotImplementedError

    def maak_zaakdocument_met_inhoud(self, document, zaak_url=None, filename=None, sender=None, stream=None, content_type=None):
        raise NotImplementedError

    def geef_inhoud(self, document):
        raise NotImplementedError

    def zet_inhoud(self, document, stream, content_type=None, checkout_id=None):
        raise NotImplementedError

    def relateer_aan_zaak(self, document, zaak_url):
        raise NotImplementedError

    def update_zaakdocument(self, document, checkout_id=None, inhoud=None):
        raise NotImplementedError

    def checkout(self, document):
        raise NotImplementedError

    def cancel_checkout(self, document, checkout_id):
        raise NotImplementedError

    def ontkoppel_zaakdocument(self, document, zaak_url):
        raise NotImplementedError

    def is_locked(self, document):
        raise NotImplementedError

    def verwijder_document(self, document):
        raise NotImplementedError

    def sync(self, dryrun=False):
        raise NotImplementedError
