from django.conf import settings
from django.urls import reverse

from import_class import import_class


class DjangoDRCStorageBackend(import_class(settings.ABSTRACT_BASE_CLASS)):
    """
    This is the backend that is used to store the documents in a CMIS compatible backend.
    """
    def create_document(self, validated_data, inhoud):
        from drc.datamodel.models import EnkelvoudigInformatieObject
        eio = EnkelvoudigInformatieObject(**validated_data)
        eio.inhoud = inhoud
        eio.save()
        return eio

    def get_documents(self):
        from drc.datamodel.models import EnkelvoudigInformatieObject
        eios = EnkelvoudigInformatieObject.objects.all()
        documents = []
        for eio in eios:
            doc = self.prepare_document(eio)
            documents.append(doc)
        return documents

    def update_document(self, validated_data, identificatie, inhoud):
        from drc.datamodel.models import EnkelvoudigInformatieObject
        eio = EnkelvoudigInformatieObject.objects.get(identificatie=identificatie)

        # TODO: Update the values
        eio.save()
        return eio

    def get_document(self, identificatie):
        from drc.datamodel.models import EnkelvoudigInformatieObject
        eio = EnkelvoudigInformatieObject.objects.get(identificatie=identificatie)
        return self.prepare_document(eio)

    def prepare_document(self, eio):
        print(eio.inhoud.url)
        document = {
            "url": "{}{}".format(settings.HOST_URL, reverse('enkelvoudiginformatieobjecten-detail', kwargs={'version': '1', 'uuid': eio.identificatie})),
            "inhoud": "{}{}".format(settings.HOST_URL, eio.inhoud.url),
            "creatiedatum": eio.creatiedatum,
            "ontvangstdatum": eio.ontvangstdatum,
            "verzenddatum": eio.verzenddatum,
            "integriteit_datum": eio.integriteit_datum,
            "titel": eio.titel,
            "identificatie": eio.identificatie,
            "bronorganisatie": eio.bronorganisatie,
            "vertrouwelijkaanduiding": eio.vertrouwelijkheidaanduiding,
            "auteur": eio.auteur,
            "status": eio.status,
            "beschrijving": eio.beschrijving,
            "indicatie_gebruiksrecht": eio.indicatie_gebruiksrecht,
            "ondertekening_soort": eio.ondertekening_soort,
            "ondertekening_datum": eio.ondertekening_datum,
            "informatieobjecttype": eio.informatieobjecttype,
            "formaat": eio.formaat,
            "taal": eio.taal,
            "bestandsnaam": eio.bestandsnaam,
            "link": eio.link,
            "integriteit_algoritme": eio.integriteit_algoritme,
            "integriteit_waarde": eio.integriteit_waarde,
            "bestandsomvang": eio.inhoud.size,
        }
        return document
