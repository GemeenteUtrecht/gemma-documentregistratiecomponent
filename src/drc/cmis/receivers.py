from django.conf import settings
from django.dispatch import receiver

from drc.cmis.client import default_client

from .signals import (
    creeer_document, creeer_zaakfolder_en_verplaats_document, update_document
)
from .storage import BinaireInhoud


@receiver(creeer_document)
def handle_creeer_document(sender, document, **kwargs):
    default_client.maak_zaakdocument_met_inhoud(
        document=document,
        zaak_url=None,
        filename=None,
        sender=settings.CMIS_SENDER_PROPERTY,
        stream=document.inhoud
    )


@receiver(update_document)
def handle_update_document(sender, document, **kwargs):
    default_client.update_zaakdocument(
        document=document, inhoud=BinaireInhoud(document.inhoud.read(), document.bestandsnaam)
    )


@receiver(creeer_zaakfolder_en_verplaats_document)
def handle_creeer_zaakfolder_en_verplaats_document(sender, zaak_url, document, **kwargs):
    default_client.creeer_zaakfolder(zaak_url)
    default_client.relateer_aan_zaak(document, zaak_url)
