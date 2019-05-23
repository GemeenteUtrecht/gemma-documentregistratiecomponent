"""
Serializers of the Document Registratie Component REST API
"""
import logging

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_text
from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _

from drf_extra_fields.fields import Base64FileField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.settings import api_settings
from vng_api_common.constants import ObjectTypes, VertrouwelijkheidsAanduiding
from vng_api_common.fields import LANGUAGE_CHOICES
from vng_api_common.models import APICredential
from vng_api_common.serializers import GegevensGroepSerializer
from vng_api_common.validators import IsImmutableValidator, URLValidator

from drc.backend import drc_storage_adapter
from drc.datamodel.constants import RelatieAarden, Statussen
from drc.datamodel.models import (
    EnkelvoudigInformatieObject, Gebruiksrechten, ObjectInformatieObject
)
from drc.sync.signals import SyncError

from .auth import get_zrc_auth

logger = logging.getLogger(__name__)


class AnyFileType:
    def __contains__(self, item):
        return True


class AnyBase64File(Base64FileField):
    ALLOWED_TYPES = AnyFileType()

    def get_file_extension(self, filename, decoded_file):
        return "bin"


class IntegriteitSerializer(GegevensGroepSerializer):
    class Meta:
        model = EnkelvoudigInformatieObject
        gegevensgroep = 'integriteit'


class OndertekeningSerializer(GegevensGroepSerializer):
    class Meta:
        model = EnkelvoudigInformatieObject
        gegevensgroep = 'ondertekening'


class EnkelvoudigInformatieObjectSerializer(serializers.Serializer):
    identificatie = serializers.CharField(required=False, max_length=40, allow_blank=True, allow_null=True, help_text='Een binnen een gegeven context ondubbelzinnige referentie naar het INFORMATIEOBJECT.')
    bronorganisatie = serializers.CharField(max_length=9, allow_blank=True, allow_null=True, help_text='Het RSIN van de Niet-natuurlijk persoon zijnde de organisatie die het informatieobject heeft gecreëerd of heeft ontvangen en als eerste in een samenwerkingsketen heeft vastgelegd.')
    creatiedatum = serializers.DateField(allow_null=True, help_text='Een datum of een gebeurtenis in de levenscyclus van het INFORMATIEOBJECT.')
    titel = serializers.CharField(max_length=200, allow_blank=True, allow_null=True, help_text='De naam waaronder het INFORMATIEOBJECT formeel bekend is.')
    vertrouwelijkheidaanduiding = serializers.ChoiceField(choices=VertrouwelijkheidsAanduiding.choices, default=VertrouwelijkheidsAanduiding.openbaar, help_text='Aanduiding van de mate waarin het INFORMATIEOBJECT voor de openbaarheid bestemd is.')
    auteur = serializers.CharField(max_length=200, allow_blank=True, allow_null=True, help_text='De persoon of organisatie die in de eerste plaats verantwoordelijk is voor het creëren van de inhoud van het INFORMATIEOBJECT.')
    status = serializers.ChoiceField(choices=Statussen.choices, required=False, allow_blank=True, allow_null=True, help_text="Aanduiding van de stand van zaken van een INFORMATIEOBJECT. De waarden 'in bewerking' en 'ter vaststelling' komen niet voor als het attribuut ontvangstdatum van een waarde is voorzien. Wijziging van de Status in 'gearchiveerd' impliceert dat het informatieobject een duurzaam, niet-wijzigbaar Formaat dient te hebben.")
    formaat = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True, help_text='De code voor de wijze waarop de inhoud van het ENKELVOUDIG INFORMATIEOBJECT is vastgelegd in een computerbestand.')
    taal = serializers.ChoiceField(choices=LANGUAGE_CHOICES, allow_blank=True, allow_null=True, help_text='Een taal van de intellectuele inhoud van het ENKELVOUDIG INFORMATIEOBJECT. De waardes komen uit ISO 639-2/B')
    bestandsnaam = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True, help_text='De naam van het fysieke bestand waarin de inhoud van het informatieobject is vastgelegd, inclusief extensie.')
    inhoud = AnyBase64File()
    link = serializers.URLField(max_length=200, required=False, allow_blank=True, allow_null=True, help_text='De URL waarmee de inhoud van het INFORMATIEOBJECT op te vragen is.')
    beschrijving = serializers.CharField(max_length=1000, required=False, allow_blank=True, allow_null=True, help_text='Een generieke beschrijving van de inhoud van het INFORMATIEOBJECT.')
    ontvangstdatum = serializers.DateField(required=False, allow_null=True, help_text='De datum waarop het INFORMATIEOBJECT ontvangen is. Verplicht te registreren voor INFORMATIEOBJECTen die van buiten de zaakbehandelende organisatie(s) ontvangen zijn. Ontvangst en verzending is voorbehouden aan documenten die van of naar andere personen ontvangen of verzonden zijn waarbij die personen niet deel uit maken van de behandeling van de zaak waarin het document een rol speelt.')
    verzenddatum = serializers.DateField(required=False, allow_null=True, help_text='De datum waarop het INFORMATIEOBJECT verzonden is, zoals deze op het INFORMATIEOBJECT vermeld is. Dit geldt voor zowel inkomende als uitgaande INFORMATIEOBJECTen. Eenzelfde informatieobject kan niet tegelijk inkomend en uitgaand zijn. Ontvangst en verzending is voorbehouden aan documenten die van of naar andere personen ontvangen of verzonden zijn waarbij die personen niet deel uit maken van de behandeling van de zaak waarin het document een rol speelt.')
    indicatie_gebruiksrecht = serializers.NullBooleanField(required=False, help_text="Indicatie of er beperkingen gelden aangaande het gebruik van het informatieobject anders dan raadpleging. Dit veld mag 'null' zijn om aan te geven dat de indicatie nog niet bekend is. Als de indicatie gezet is, dan kan je de gebruiksrechten die van toepassing zijn raadplegen via de Gebruiksrechten resource.")
    # TODO: validator!
    # ondertekening = OndertekeningSerializer(
    #     label=_("ondertekening"), allow_null=True, required=False,
    #     help_text=_("Aanduiding van de rechtskracht van een informatieobject. Mag niet van een waarde "
    #                 "zijn voorzien als de `status` de waarde 'in bewerking' of 'ter vaststelling' heeft.")
    # )
    # integriteit = IntegriteitSerializer(
    #     label=_("integriteit"), allow_null=True, required=False,
    #     help_text=_("Uitdrukking van mate van volledigheid en onbeschadigd zijn van digitaal bestand.")
    # )
    # TODO: Validate that the urls are validated against the ZTC
    informatieobjecttype = serializers.URLField(max_length=200, allow_null=True, help_text='URL naar de INFORMATIEOBJECTTYPE in het ZTC.')

    def create(self):
        """
        Handle the create calls.
        """
        drc_storage_adapter.create_enkelvoudiginformatieobject(self.validated_data.copy())
        return None

    def update(self, identificatie):
        """
        Handle the update calls.
        """
        drc_storage_adapter.update_enkelvoudiginformatieobject(self.validated_data.copy(), identificatie)
        return None


class RetrieveEnkelvoudigInformatieObjectSerializer(serializers.Serializer):
    url = serializers.URLField(max_length=200, allow_blank=True, allow_null=True)
    identificatie = serializers.CharField(required=False, max_length=40, allow_blank=True, allow_null=True, help_text='Een binnen een gegeven context ondubbelzinnige referentie naar het INFORMATIEOBJECT.')
    bronorganisatie = serializers.CharField(max_length=9, allow_blank=True, allow_null=True, help_text='Het RSIN van de Niet-natuurlijk persoon zijnde de organisatie die het informatieobject heeft gecreëerd of heeft ontvangen en als eerste in een samenwerkingsketen heeft vastgelegd.')
    creatiedatum = serializers.DateField(allow_null=True, help_text='Een datum of een gebeurtenis in de levenscyclus van het INFORMATIEOBJECT.')
    titel = serializers.CharField(max_length=200, allow_blank=True, allow_null=True, help_text='De naam waaronder het INFORMATIEOBJECT formeel bekend is.')
    vertrouwelijkheidaanduiding = serializers.ChoiceField(choices=VertrouwelijkheidsAanduiding.choices, default=VertrouwelijkheidsAanduiding.openbaar, help_text='Aanduiding van de mate waarin het INFORMATIEOBJECT voor de openbaarheid bestemd is.')
    auteur = serializers.CharField(max_length=200, allow_blank=True, allow_null=True, help_text='De persoon of organisatie die in de eerste plaats verantwoordelijk is voor het creëren van de inhoud van het INFORMATIEOBJECT.')
    status = serializers.ChoiceField(choices=Statussen.choices, required=False, allow_blank=True, allow_null=True, help_text="Aanduiding van de stand van zaken van een INFORMATIEOBJECT. De waarden 'in bewerking' en 'ter vaststelling' komen niet voor als het attribuut ontvangstdatum van een waarde is voorzien. Wijziging van de Status in 'gearchiveerd' impliceert dat het informatieobject een duurzaam, niet-wijzigbaar Formaat dient te hebben.")
    formaat = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True, help_text='De code voor de wijze waarop de inhoud van het ENKELVOUDIG INFORMATIEOBJECT is vastgelegd in een computerbestand.')
    taal = serializers.ChoiceField(choices=LANGUAGE_CHOICES, allow_blank=True, allow_null=True, help_text='Een taal van de intellectuele inhoud van het ENKELVOUDIG INFORMATIEOBJECT. De waardes komen uit ISO 639-2/B')
    bestandsnaam = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True, help_text='De naam van het fysieke bestand waarin de inhoud van het informatieobject is vastgelegd, inclusief extensie.')
    inhoud = serializers.URLField()
    bestandsomvang = serializers.IntegerField(min_value=0)
    link = serializers.URLField(max_length=200, required=False, allow_blank=True, allow_null=True, help_text='De URL waarmee de inhoud van het INFORMATIEOBJECT op te vragen is.')
    beschrijving = serializers.CharField(max_length=1000, required=False, allow_blank=True, allow_null=True, help_text='Een generieke beschrijving van de inhoud van het INFORMATIEOBJECT.')
    ontvangstdatum = serializers.DateField(required=False, allow_null=True, help_text='De datum waarop het INFORMATIEOBJECT ontvangen is. Verplicht te registreren voor INFORMATIEOBJECTen die van buiten de zaakbehandelende organisatie(s) ontvangen zijn. Ontvangst en verzending is voorbehouden aan documenten die van of naar andere personen ontvangen of verzonden zijn waarbij die personen niet deel uit maken van de behandeling van de zaak waarin het document een rol speelt.')
    verzenddatum = serializers.DateField(required=False, allow_null=True, help_text='De datum waarop het INFORMATIEOBJECT verzonden is, zoals deze op het INFORMATIEOBJECT vermeld is. Dit geldt voor zowel inkomende als uitgaande INFORMATIEOBJECTen. Eenzelfde informatieobject kan niet tegelijk inkomend en uitgaand zijn. Ontvangst en verzending is voorbehouden aan documenten die van of naar andere personen ontvangen of verzonden zijn waarbij die personen niet deel uit maken van de behandeling van de zaak waarin het document een rol speelt.')
    indicatie_gebruiksrecht = serializers.NullBooleanField(required=False, help_text="Indicatie of er beperkingen gelden aangaande het gebruik van het informatieobject anders dan raadpleging. Dit veld mag 'null' zijn om aan te geven dat de indicatie nog niet bekend is. Als de indicatie gezet is, dan kan je de gebruiksrechten die van toepassing zijn raadplegen via de Gebruiksrechten resource.")
    # TODO: validator!
    # ondertekening = OndertekeningSerializer(
    #     label=_("ondertekening"), allow_null=True, required=False,
    #     help_text=_("Aanduiding van de rechtskracht van een informatieobject. Mag niet van een waarde "
    #                 "zijn voorzien als de `status` de waarde 'in bewerking' of 'ter vaststelling' heeft.")
    # )
    # integriteit = IntegriteitSerializer(
    #     label=_("integriteit"), allow_null=True, required=False,
    #     help_text=_("Uitdrukking van mate van volledigheid en onbeschadigd zijn van digitaal bestand.")
    # )
    # TODO: Validate that the urls are validated against the ZTC
    informatieobjecttype = serializers.URLField(max_length=200, allow_null=True, help_text='URL naar de INFORMATIEOBJECTTYPE in het ZTC.')

    def create(self):
        """
        Handle the create calls.
        """
        drc_storage_adapter.create_enkelvoudiginformatieobject(self.validated_data.copy())
        return None

    def update(self, identificatie):
        """
        Handle the update calls.
        """
        drc_storage_adapter.update_enkelvoudiginformatieobject(self.validated_data.copy(), identificatie)
        return None

# class EnkelvoudigInformatieObjectSerializer(serializers.HyperlinkedModelSerializer):
#     """
#     Serializer for the EnkelvoudigInformatieObject model
#     """
#     inhoud = AnyBase64File()
#     bestandsomvang = serializers.IntegerField(
#         source='inhoud.size', read_only=True,
#         min_value=0
#     )
#     integriteit = IntegriteitSerializer(
#         label=_("integriteit"), allow_null=True, required=False,
#         help_text=_("Uitdrukking van mate van volledigheid en onbeschadigd zijn van digitaal bestand.")
#     )
#     # TODO: validator!
#     ondertekening = OndertekeningSerializer(
#         label=_("ondertekening"), allow_null=True, required=False,
#         help_text=_("Aanduiding van de rechtskracht van een informatieobject. Mag niet van een waarde "
#                     "zijn voorzien als de `status` de waarde 'in bewerking' of 'ter vaststelling' heeft.")
#     )

#     class Meta:
#         model = EnkelvoudigInformatieObject
#         fields = (
#             'url',
#             'identificatie',
#             'bronorganisatie',
#             'creatiedatum',
#             'titel',
#             'vertrouwelijkheidaanduiding',
#             'auteur',
#             'status',
#             'formaat',
#             'taal',
#             'bestandsnaam',
#             'inhoud',
#             'bestandsomvang',
#             'link',
#             'beschrijving',
#             'ontvangstdatum',
#             'verzenddatum',
#             'indicatie_gebruiksrecht',
#             'ondertekening',
#             'integriteit',
#             'informatieobjecttype'  # van-relatie
#         )
#         extra_kwargs = {
#             'url': {
#                 'lookup_field': 'uuid',
#             },
#             'informatieobjecttype': {
#                 'validators': [URLValidator(get_auth=get_ztc_auth)],
#             }
#         }
#         validators = [StatusValidator()]

#     def to_representation(self, instance):
#         data = super().to_representation(instance)
#         data['inhoud'] = self.get_file(instance)
#         data['auteur'] = self.get_from_temp_doc(instance, 'auteur')
#         data['bestandsnaam'] = self.get_from_temp_doc(instance, 'bestandsnaam')
#         data['creatiedatum'] = self.get_from_temp_doc(instance, 'creatiedatum')
#         data['vertrouwelijkheidaanduiding'] = self.get_from_temp_doc(instance, 'vertrouwelijkheidaanduiding')
#         data['taal'] = self.get_from_temp_doc(instance, 'taal')
#         return data

#     def get_file(self, obj):
#         from drc.backend import drc_storage_adapter

#         document = drc_storage_adapter.get_document(obj)
#         if document:
#             host = get_current_site(None).domain
#             schema = 'https' if settings.IS_HTTPS else 'http'
#             return f'{schema}://{host}{document.url}'
#         return None

#     def get_from_temp_doc(self, obj, attr_name):
#         from drc.backend import drc_storage_adapter
#         document = drc_storage_adapter.get_document(obj)
#         if document:
#             return getattr(document, attr_name)
#         return None

#     def _get_informatieobjecttype(self, informatieobjecttype_url: str) -> dict:
#         if not hasattr(self, 'informatieobjecttype'):
#             # dynamic so that it can be mocked in tests easily
#             Client = import_string(settings.ZDS_CLIENT_CLASS)
#             client = Client.from_url(informatieobjecttype_url)
#             client.auth = APICredential.get_auth(
#                 informatieobjecttype_url,
#                 scopes=['zds.scopes.zaaktypes.lezen']
#             )
#             self._informatieobjecttype = client.request(informatieobjecttype_url, 'informatieobjecttype')
#         return self._informatieobjecttype

#     def validate_indicatie_gebruiksrecht(self, indicatie):
#         if self.instance and not indicatie and self.instance.gebruiksrechten_set.exists():
#             raise serializers.ValidationError(
#                 _("De indicatie kan niet weggehaald worden of ongespecifieerd "
#                   "zijn als er Gebruiksrechten gedefinieerd zijn."),
#                 code='existing-gebruiksrechten'
#             )
#         # create: not self.instance or update: usage_rights exists
#         elif indicatie and (not self.instance or not self.instance.gebruiksrechten_set.exists()):
#             raise serializers.ValidationError(
#                 _("De indicatie moet op 'ja' gezet worden door `gebruiksrechten` "
#                   "aan te maken, dit kan niet direct op deze resource."),
#                 code='missing-gebruiksrechten'
#             )
#         return indicatie

#     def create(self, validated_data):
#         """
#         Handle nested writes.
#         """
#         integriteit = validated_data.pop('integriteit', None)
#         ondertekening = validated_data.pop('ondertekening', None)

#         # add vertrouwelijkheidaanduiding
#         if 'vertrouwelijkheidaanduiding' not in validated_data:
#             informatieobjecttype = self._get_informatieobjecttype(validated_data['informatieobjecttype'])
#             validated_data['vertrouwelijkheidaanduiding'] = informatieobjecttype['vertrouwelijkheidaanduiding']

#         eio = super().create(validated_data)
#         eio.integriteit = integriteit
#         eio.ondertekening = ondertekening
#         eio.save()

#         try:
#             drc_storage_adapter.create_document(eio, eio.inhoud, eio.link)
#         except ValueError as val_error:
#             logger.error(val_error)
#             eio.delete()
#             raise serializer.ValidationError(
#                 'Dit is een foutje!'
#             )

#         return eio

#     def update(self, instance, validated_data):
#         """
#         Handle nested writes.
#         """
#         instance.integriteit = validated_data.pop('integriteit', None)
#         instance.ondertekening = validated_data.pop('ondertekening', None)
#         eio = super().update(instance, validated_data)

#         drc_storage_adapter.update_document(eio, None, eio.inhoud, eio.link)

#         return eio


class ObjectInformatieObjectSerializer(serializers.HyperlinkedModelSerializer):
    aard_relatie_weergave = serializers.ChoiceField(
        source='get_aard_relatie_display', read_only=True,
        choices=[(force_text(value), key) for key, value in RelatieAarden.choices]
    )

    # TODO: valideer dat ObjectInformatieObject.informatieobjecttype hoort
    # bij zaak.zaaktype
    class Meta:
        model = ObjectInformatieObject
        fields = (
            'url',
            'informatieobject',
            'object',
            'object_type',
            'aard_relatie_weergave',
            'titel',
            'beschrijving',
            'registratiedatum',
        )
        extra_kwargs = {
            'url': {
                'lookup_field': 'uuid',
            },
            'informatieobject': {
                'lookup_field': 'uuid',
                'validators': [IsImmutableValidator()],
            },
            'object': {
                'validators': [
                    URLValidator(get_auth=get_zrc_auth, headers={'Accept-Crs': 'EPSG:4326'}),
                    IsImmutableValidator(),
                ],
            },
            'object_type': {
                'validators': [IsImmutableValidator()]
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not hasattr(self, 'initial_data'):
            return

        object_type = self.initial_data.get('object_type')

        if object_type == ObjectTypes.besluit:
            del self.fields['titel']
            del self.fields['beschrijving']
            del self.fields['registratiedatum']

    def save(self, **kwargs):
        # can't slap a transaction atomic on this, since ZRC/BRC query for the
        # relation!
        try:
            return super().save(**kwargs)
        except SyncError as sync_error:
            # delete the object again
            ObjectInformatieObject.objects.filter(
                informatieobject=self.validated_data['informatieobject'],
                object=self.validated_data['object']
            )._raw_delete('default')
            raise serializers.ValidationError({
                api_settings.NON_FIELD_ERRORS_KEY: sync_error.args[0]
            }) from sync_error

    def create(self, validated_data):
        """
        Handle backend calls.
        """
        oio = super().create(validated_data)

        try:
            drc_storage_adapter.create_folder(oio.object)
            drc_storage_adapter.move_document(oio.informatieobject, oio.object)
        except ValueError as val_error:
            logger.error(val_error)
            oio.delete()

        return oio

    def update(self, instance, validated_data):
        """
        Handle backend calls.
        """
        old_location = instance.object

        oio = super().update(instance, validated_data)

        if old_location != oio.object:
            drc_storage_adapter.create_folder(oio.object)
            drc_storage_adapter.move_document(oio.informatieobject, oio.object)

        return oio


class GebruiksrechtenSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Gebruiksrechten
        fields = (
            'url',
            'informatieobject',
            'startdatum',
            'einddatum',
            'omschrijving_voorwaarden'
        )
        extra_kwargs = {
            'url': {
                'lookup_field': 'uuid',
            },
            'informatieobject': {
                'lookup_field': 'uuid',
                'validators': [IsImmutableValidator()],
            },
        }
