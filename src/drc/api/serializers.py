"""
Serializers of the Document Registratie Component REST API
"""
import logging

from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from drf_extra_fields.fields import Base64FileField
from rest_framework import serializers
from rest_framework.settings import api_settings
from vng_api_common.constants import ObjectTypes, VertrouwelijkheidsAanduiding
from vng_api_common.fields import LANGUAGE_CHOICES
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


class BaseEnkelvoudigInformatieObjectSerializer(serializers.Serializer):
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
    link = serializers.URLField(max_length=200, required=False, allow_blank=True, allow_null=True, help_text='De URL waarmee de inhoud van het INFORMATIEOBJECT op te vragen is.')
    beschrijving = serializers.CharField(max_length=1000, required=False, allow_blank=True, allow_null=True, help_text='Een generieke beschrijving van de inhoud van het INFORMATIEOBJECT.')
    ontvangstdatum = serializers.DateField(required=False, allow_null=True, help_text='De datum waarop het INFORMATIEOBJECT ontvangen is. Verplicht te registreren voor INFORMATIEOBJECTen die van buiten de zaakbehandelende organisatie(s) ontvangen zijn. Ontvangst en verzending is voorbehouden aan documenten die van of naar andere personen ontvangen of verzonden zijn waarbij die personen niet deel uit maken van de behandeling van de zaak waarin het document een rol speelt.')
    verzenddatum = serializers.DateField(required=False, allow_null=True, help_text='De datum waarop het INFORMATIEOBJECT verzonden is, zoals deze op het INFORMATIEOBJECT vermeld is. Dit geldt voor zowel inkomende als uitgaande INFORMATIEOBJECTen. Eenzelfde informatieobject kan niet tegelijk inkomend en uitgaand zijn. Ontvangst en verzending is voorbehouden aan documenten die van of naar andere personen ontvangen of verzonden zijn waarbij die personen niet deel uit maken van de behandeling van de zaak waarin het document een rol speelt.')
    indicatie_gebruiksrecht = serializers.NullBooleanField(required=False, help_text="Indicatie of er beperkingen gelden aangaande het gebruik van het informatieobject anders dan raadpleging. Dit veld mag 'null' zijn om aan te geven dat de indicatie nog niet bekend is. Als de indicatie gezet is, dan kan je de gebruiksrechten die van toepassing zijn raadplegen via de Gebruiksrechten resource.")
    informatieobjecttype = serializers.URLField(max_length=200, allow_null=True, help_text='URL naar de INFORMATIEOBJECTTYPE in het ZTC.')
    ondertekening = OndertekeningSerializer(
        label=_("ondertekening"), allow_null=True, required=False,
        help_text=_("Aanduiding van de rechtskracht van een informatieobject. Mag niet van een waarde "
                    "zijn voorzien als de `status` de waarde 'in bewerking' of 'ter vaststelling' heeft.")
    )
    # integriteit = IntegriteitSerializer(
    #     label=_("integriteit"), allow_null=True, required=False,
    #     help_text=_("Uitdrukking van mate van volledigheid en onbeschadigd zijn van digitaal bestand.")
    # )
    # TODO: Validate that the urls are validated against the ZTC


class EnkelvoudigInformatieObjectSerializer(BaseEnkelvoudigInformatieObjectSerializer):
    inhoud = AnyBase64File()

    def create(self):
        """
        Handle the create calls.
        """
        doc = drc_storage_adapter.create_enkelvoudiginformatieobject(self.validated_data.copy())
        return doc

    def update(self, identificatie):
        """
        Handle the update calls.
        """
        return drc_storage_adapter.update_enkelvoudiginformatieobject(self.validated_data.copy(), identificatie)


class RetrieveEnkelvoudigInformatieObjectSerializer(BaseEnkelvoudigInformatieObjectSerializer):
    # Add extra fields that are used in the return
    url = serializers.URLField(max_length=200, allow_blank=True, allow_null=True)
    inhoud = serializers.URLField(max_length=200, allow_blank=True, allow_null=True)
    bestandsomvang = serializers.IntegerField(min_value=0)

    def create(self):
        raise NotImplementedError('This should not be used')

    def update(self, identificatie):
        raise NotImplementedError('This should not be used')


class ObjectInformatieObjectSerializer(serializers.Serializer):
    url = serializers.URLField(allow_blank=True, allow_null=True, required=False)
    informatieobject = serializers.URLField(allow_blank=True, allow_null=True)
    object = serializers.URLField(max_length=200, allow_blank=True, allow_null=True, help_text="URL naar het gerelateerde OBJECT.")
    object_type = serializers.ChoiceField(allow_blank=True, allow_null=True, choices=ObjectTypes.choices)
    aard_relatie_weergave = serializers.ChoiceField(
        read_only=True, choices=[(force_text(value), key) for key, value in RelatieAarden.choices]
    )
    titel = serializers.CharField(max_length=200, allow_blank=True, allow_null=True, required=False, help_text='De naam waaronder het INFORMATIEOBJECT binnen het OBJECT bekend is.')
    beschrijving = serializers.CharField(required=False, allow_blank=True)
    registratiedatum = serializers.DateTimeField(read_only=True, allow_null=True, help_text='De datum waarop de behandelende organisatie het INFORMATIEOBJECT heeft geregistreerd bij het OBJECT. Geldige waardes zijn datumtijden gelegen op of voor de huidige datum en tijd.')

    # TODO: valideer dat ObjectInformatieObject.informatieobjecttype hoort
    # bij zaak.zaaktype
    class Meta:
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

        if isinstance(self.initial_data, list):
            for initial_data in self.initial_data:
                self.check_data(initial_data)
        else:
            self.check_data(self.initial_data)

    def check_data(self, initial_data):
        object_type = initial_data.get('object_type')

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

    def create(self):
        """
        Handle backend calls.
        """
        drc_storage_adapter.create_objectinformatieobject(self.validated_data.copy())

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


# class ObjectInformatieObjectSerializer(serializers.HyperlinkedModelSerializer):
#     aard_relatie_weergave = serializers.ChoiceField(
#         source='get_aard_relatie_display', read_only=True,
#         choices=[(force_text(value), key) for key, value in RelatieAarden.choices]
#     )

#     # TODO: valideer dat ObjectInformatieObject.informatieobjecttype hoort
#     # bij zaak.zaaktype
#     class Meta:
#         model = ObjectInformatieObject
#         fields = (
#             'url',
#             'informatieobject',
#             'object',
#             'object_type',
#             'aard_relatie_weergave',
#             'titel',
#             'beschrijving',
#             'registratiedatum',
#         )
#         extra_kwargs = {
#             'url': {
#                 'lookup_field': 'uuid',
#             },
#             'informatieobject': {
#                 'lookup_field': 'uuid',
#                 'validators': [IsImmutableValidator()],
#             },
#             'object': {
#                 'validators': [
#                     URLValidator(get_auth=get_zrc_auth, headers={'Accept-Crs': 'EPSG:4326'}),
#                     IsImmutableValidator(),
#                 ],
#             },
#             'object_type': {
#                 'validators': [IsImmutableValidator()]
#             }
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         if not hasattr(self, 'initial_data'):
#             return

#         object_type = self.initial_data.get('object_type')

#         if object_type == ObjectTypes.besluit:
#             del self.fields['titel']
#             del self.fields['beschrijving']
#             del self.fields['registratiedatum']

#     def save(self, **kwargs):
#         # can't slap a transaction atomic on this, since ZRC/BRC query for the
#         # relation!
#         try:
#             return super().save(**kwargs)
#         except SyncError as sync_error:
#             # delete the object again
#             ObjectInformatieObject.objects.filter(
#                 informatieobject=self.validated_data['informatieobject'],
#                 object=self.validated_data['object']
#             )._raw_delete('default')
#             raise serializers.ValidationError({
#                 api_settings.NON_FIELD_ERRORS_KEY: sync_error.args[0]
#             }) from sync_error

#     def create(self, validated_data):
#         """
#         Handle backend calls.
#         """
#         oio = super().create(validated_data)

#         try:
#             drc_storage_adapter.create_folder(oio.object)
#             drc_storage_adapter.move_document(oio.informatieobject, oio.object)
#         except ValueError as val_error:
#             logger.error(val_error)
#             oio.delete()

#         return oio

#     def update(self, instance, validated_data):
#         """
#         Handle backend calls.
#         """
#         old_location = instance.object

#         oio = super().update(instance, validated_data)

#         if old_location != oio.object:
#             drc_storage_adapter.create_folder(oio.object)
#             drc_storage_adapter.move_document(oio.informatieobject, oio.object)

#         return oio


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
