# from django.conf import settings
# from django.db.models.signals import post_save
# from django.dispatch import receiver

# from drc.cmis.client import default_client
# from drc.datamodel.models import (
#     EnkelvoudigInformatieObject, ObjectInformatieObject
# )

# from .storage import BinaireInhoud


# @receiver(post_save, sender=EnkelvoudigInformatieObject)
# def handle_creeer_document(sender, instance, created, update_fields=None, **kwargs):
#     print(sender, instance, created, update_fields, kwargs)
#     if created:
#         default_client.maak_zaakdocument_met_inhoud(
#             document=instance,
#             zaak_url=None,
#             filename=None,
#             sender=settings.CMIS_SENDER_PROPERTY,
#             stream=instance.inhoud
#         )
#     elif not update_fields or '_object_id' not in update_fields:
#         # TODO: Make sure that documents can be updated. Maybe hook into a pre update?
#         default_client.update_zaakdocument(
#             document=instance, inhoud=BinaireInhoud(instance.inhoud.read(), instance.bestandsnaam)
#         )


# # TODO: See what will be posible here
# # @receiver(post_save, sender=ObjectInformatieObject)
# # def handle_creeer_zaakfolder_en_verplaats_document(sender, instance, created, **kwargs):
# #     if created:
# #         default_client.creeer_zaakfolder(instance.object)
# #         if instance.informatieobject:
# #             default_client.relateer_aan_zaak(instance.informatieobject, instance.object)
