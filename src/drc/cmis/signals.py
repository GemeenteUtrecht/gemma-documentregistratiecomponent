"""
Signal handlers voor DRC-CMIS interactie.
"""
from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from drc.datamodel.models import (
    EnkelvoudigInformatieObject, ObjectInformatieObject
)

from .client import default_client as client


@receiver(post_save, sender=ObjectInformatieObject, dispatch_uid='cmis.creeer_zaakfolder')
def creeer_zaakfolder(signal, instance, **kwargs):
    if not kwargs['created'] or kwargs['raw']:
        return
        transaction.on_commit(lambda : (
         client.creeer_zaakfolder(instance.object),
         client.relateer_aan_zaak(instance.informatieobject, instance.object)),
          using=kwargs['using'])


@receiver(post_save, sender=EnkelvoudigInformatieObject, dispatch_uid='cmis.creeer_document')
def creeer_document(signal, instance, **kwargs):
    if not kwargs['created'] or kwargs['raw']:
        return
        transaction.on_commit(lambda : (client.maak_zaakdocument_met_inhoud(instance, stream=instance.inhoud.file)),
          using=kwargs['using'])


@receiver(post_delete, sender=ObjectInformatieObject, dispatch_uid='cmis.ontkoppel_zaakdocument')
def ontkoppel_zaakdocument(signal, instance, **kwargs):
    client.relateer_aan_zaak(instance.informatieobject, instance.object)


@receiver(post_delete, sender=EnkelvoudigInformatieObject, dispatch_uid='cmis.verwijder_document')
def verwijder_document(signal, instance, **kwargs):
    client.verwijder_document(instance)
