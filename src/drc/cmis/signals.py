# TODO: create signals to create cetain things.

from django.dispatch import Signal

creeer_document = Signal(providing_args=["document"])
update_document = Signal(providing_args=["document"])
creeer_zaakfolder_en_verplaats_document = Signal(providing_args=["zaak_url", "document"])
# creeer_document = Signal(providing_args=["document"])
