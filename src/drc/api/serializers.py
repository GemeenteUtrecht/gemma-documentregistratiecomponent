"""
Serializers of the Document Registratie Component REST API
"""
import uuid

from django.conf import settings
from django.db import transaction
from django.utils.encoding import force_text
from django.utils.http import urlencode
from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _

from drf_extra_fields.fields import Base64FileField
from humanize import naturalsize
from privates.storages import PrivateMediaFileSystemStorage
from rest_framework import serializers
from rest_framework.reverse import reverse
from vng_api_common.constants import ObjectTypes, VertrouwelijkheidsAanduiding
from vng_api_common.fields import LANGUAGE_CHOICES
from vng_api_common.models import APICredential
from vng_api_common.serializers import (
    GegevensGroepSerializer, add_choice_values_help_text
)
from vng_api_common.utils import get_help_text
from vng_api_common.validators import IsImmutableValidator, URLValidator

from drc.backend import drc_storage_adapter
from drc.datamodel.constants import (
    ChecksumAlgoritmes, OndertekeningSoorten, Statussen
)
from drc.datamodel.models import (
    EnkelvoudigInformatieObject, EnkelvoudigInformatieObjectCanonical,
    Gebruiksrechten, ObjectInformatieObject
)

from .auth import get_zrc_auth, get_ztc_auth
from .validators import (
    InformatieObjectUniqueValidator, ObjectInformatieObjectValidator,
    StatusValidator
)


class AnyFileType:
    def __contains__(self, item):
        return True


class AnyBase64File(Base64FileField):
    ALLOWED_TYPES = AnyFileType()

    def __init__(self, view_name: str = None, *args, **kwargs):
        self.view_name = view_name
        super().__init__(*args, **kwargs)

    def get_file_extension(self, filename, decoded_file):
        return "bin"

    def to_representation(self, file):
        is_private_storage = isinstance(file.storage, PrivateMediaFileSystemStorage)

        if not is_private_storage or self.represent_in_base64:
            return super().to_representation(file)

        assert self.view_name, "You must pass the `view_name` kwarg for private media fields"

        model_instance = file.instance
        request = self.context.get('request')

        url_field = self.parent.fields["url"]
        lookup_field = url_field.lookup_field
        kwargs = {lookup_field: getattr(model_instance, lookup_field)}
        url = reverse(self.view_name, kwargs=kwargs, request=request)

        # Retrieve the correct version to construct the download url that
        # points to the content of that version
        instance = self.parent.instance
        # in case of pagination instance can be a list object
        if isinstance(instance, list):
            instance = instance[0]

        if hasattr(instance, 'versie'):
            versie = instance.versie
        else:
            versie = instance.get(uuid=kwargs['uuid']).versie
        query_string = urlencode({'versie': versie})
        return f'{url}?{query_string}'


class IntegriteitSerializer(serializers.Serializer):
    algoritme = serializers.ChoiceField(choices=ChecksumAlgoritmes.choices, help_text=_("Aanduiding van algoritme, gebruikt om de checksum te maken."))
    waarde = serializers.CharField(min_length=1, max_length=128, help_text=_("De waarde van de checksum."))
    datum = serializers.DateField(help_text=_("Datum waarop de checksum is gemaakt."))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        value_display_mapping = add_choice_values_help_text(ChecksumAlgoritmes)
        self.fields['algoritme'].help_text += f"\n\n{value_display_mapping}"


class OndertekeningSerializer(serializers.Serializer):
    soort = serializers.ChoiceField(choices=OndertekeningSoorten.choices, help_text=_("Aanduiding van de wijze van ondertekening van het INFORMATIEOBJECT"))
    datum = serializers.DateField(help_text=_("De datum waarop de ondertekening van het INFORMATIEOBJECT heeft plaatsgevonden."))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        value_display_mapping = add_choice_values_help_text(OndertekeningSoorten)
        self.fields['soort'].help_text += f"\n\n{value_display_mapping}"


class BaseEnkelvoudigInformatieObjectSerializer(serializers.Serializer):
    identificatie = serializers.CharField(
        required=False, max_length=40, allow_blank=True, allow_null=True,
        help_text='Een binnen een gegeven context ondubbelzinnige referentie naar het INFORMATIEOBJECT.'
    )
    bronorganisatie = serializers.CharField(
        max_length=9, allow_blank=True, allow_null=True,
        help_text=_('Het RSIN van de Niet-natuurlijk persoon zijnde de organisatie die het informatieobject'
                    ' heeft gecreëerd of heeft ontvangen en als eerste in een samenwerkingsketen heeft vastgelegd.')
    )
    creatiedatum = serializers.DateField(
        allow_null=True, help_text='Een datum of een gebeurtenis in de levenscyclus van het INFORMATIEOBJECT.'
    )
    titel = serializers.CharField(
        max_length=200, allow_blank=True, allow_null=True,
        help_text='De naam waaronder het INFORMATIEOBJECT formeel bekend is.'
    )
    vertrouwelijkheidaanduiding = serializers.ChoiceField(
        choices=VertrouwelijkheidsAanduiding.choices, default=VertrouwelijkheidsAanduiding.openbaar,
        help_text='Aanduiding van de mate waarin het INFORMATIEOBJECT voor de openbaarheid bestemd is.'
    )
    auteur = serializers.CharField(
        max_length=200, allow_blank=True, allow_null=True,
        help_text='De persoon of organisatie die in de eerste plaats verantwoordelijk is voor het creëren van de inhoud van het INFORMATIEOBJECT.'
    )
    status = serializers.ChoiceField(
        choices=Statussen.choices, required=False, allow_blank=True, allow_null=True,
        validators=[StatusValidator()],
        help_text=_("Aanduiding van de stand van zaken van een INFORMATIEOBJECT. De waarden 'in bewerking'"
                    " en 'ter vaststelling' komen niet voor als het attribuut ontvangstdatum van een waarde"
                    " is voorzien. Wijziging van de Status in 'gearchiveerd' impliceert dat het"
                    " informatieobject een duurzaam, niet-wijzigbaar Formaat dient te hebben.")
    )
    formaat = serializers.CharField(
        max_length=255, required=False, allow_blank=True, allow_null=True,
        help_text='De code voor de wijze waarop de inhoud van het ENKELVOUDIG INFORMATIEOBJECT is vastgelegd in een computerbestand.'
    )
    taal = serializers.ChoiceField(
        choices=LANGUAGE_CHOICES, allow_blank=True, allow_null=True,
        help_text='Een taal van de intellectuele inhoud van het ENKELVOUDIG INFORMATIEOBJECT. De waardes komen uit ISO 639-2/B'
    )
    bestandsnaam = serializers.CharField(
        max_length=255, required=False, allow_blank=True, allow_null=True,
        help_text='De naam van het fysieke bestand waarin de inhoud van het informatieobject is vastgelegd, inclusief extensie.'
    )
    link = serializers.URLField(
        max_length=200, required=False, allow_blank=True, allow_null=True,
        help_text='De URL waarmee de inhoud van het INFORMATIEOBJECT op te vragen is.'
    )
    beschrijving = serializers.CharField(
        max_length=1000, required=False, allow_blank=True, allow_null=True,
        help_text='Een generieke beschrijving van de inhoud van het INFORMATIEOBJECT.'
    )
    ontvangstdatum = serializers.DateField(
        required=False, allow_null=True,
        help_text=_('De datum waarop het INFORMATIEOBJECT ontvangen is. Verplicht te registreren voor'
                    ' INFORMATIEOBJECTen die van buiten de zaakbehandelende organisatie(s) ontvangen zijn.'
                    ' Ontvangst en verzending is voorbehouden aan documenten die van of naar andere personen'
                    ' ontvangen of verzonden zijn waarbij die personen niet deel uit maken van de behandeling'
                    ' van de zaak waarin het document een rol speelt.')
    )
    verzenddatum = serializers.DateField(
        required=False, allow_null=True,
        help_text=_('De datum waarop het INFORMATIEOBJECT verzonden is, zoals deze op het INFORMATIEOBJECT'
                    ' vermeld is. Dit geldt voor zowel inkomende als uitgaande INFORMATIEOBJECTen. Eenzelfde'
                    ' informatieobject kan niet tegelijk inkomend en uitgaand zijn. Ontvangst en verzending'
                    ' is voorbehouden aan documenten die van of naar andere personen ontvangen of verzonden'
                    ' zijn waarbij die personen niet deel uit maken van de behandeling van de zaak waarin'
                    ' het document een rol speelt.')
    )
    indicatie_gebruiksrecht = serializers.NullBooleanField(
        required=False,
        help_text=_("Indicatie of er beperkingen gelden aangaande het gebruik van het informatieobject"
                    " anders dan raadpleging. Dit veld mag 'null' zijn om aan te geven dat de indicatie"
                    " nog niet bekend is. Als de indicatie gezet is, dan kan je de gebruiksrechten die"
                    " van toepassing zijn raadplegen via de Gebruiksrechten resource.")
    )
    informatieobjecttype = serializers.URLField(
        max_length=200, allow_null=True, validators=[URLValidator(get_auth=get_ztc_auth)],
        help_text='URL naar de INFORMATIEOBJECTTYPE in het ZTC.'
    )
    ondertekening = OndertekeningSerializer(
        label=_("ondertekening"), allow_null=True, required=False,
        help_text=_("Aanduiding van de rechtskracht van een informatieobject. Mag niet van een waarde "
                    "zijn voorzien als de `status` de waarde 'in bewerking' of 'ter vaststelling' heeft.")
    )
    integriteit = IntegriteitSerializer(
        label=_("integriteit"), allow_null=True, required=False,
        help_text=_("Uitdrukking van mate van volledigheid en onbeschadigd zijn van digitaal bestand.")
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        value_display_mapping = add_choice_values_help_text(VertrouwelijkheidsAanduiding)
        self.fields['vertrouwelijkheidaanduiding'].help_text += f"\n\n{value_display_mapping}"

        value_display_mapping = add_choice_values_help_text(Statussen)
        self.fields['status'].help_text += f"\n\n{value_display_mapping}"

    def _get_informatieobjecttype(self, informatieobjecttype_url: str) -> dict:
        if not hasattr(self, 'informatieobjecttype'):
            # dynamic so that it can be mocked in tests easily
            Client = import_string(settings.ZDS_CLIENT_CLASS)
            client = Client.from_url(informatieobjecttype_url)
            client.auth = APICredential.get_auth(
                informatieobjecttype_url,
                scopes=['zds.scopes.zaaktypes.lezen']
            )
            self._informatieobjecttype = client.request(informatieobjecttype_url, 'informatieobjecttype')
        return self._informatieobjecttype

    def validate_indicatie_gebruiksrecht(self, indicatie):
        if self.instance and not indicatie and self.instance.canonical.gebruiksrechten_set.exists():
            raise serializers.ValidationError(
                _("De indicatie kan niet weggehaald worden of ongespecifieerd "
                  "zijn als er Gebruiksrechten gedefinieerd zijn."),
                code='existing-gebruiksrechten'
            )
        # create: not self.instance or update: usage_rights exists
        elif indicatie and (not self.instance or not self.instance.canonical.gebruiksrechten_set.exists()):
            raise serializers.ValidationError(
                _("De indicatie moet op 'ja' gezet worden door `gebruiksrechten` "
                  "aan te maken, dit kan niet direct op deze resource."),
                code='missing-gebruiksrechten'
            )
        return indicatie


class EnkelvoudigInformatieObjectSerializer(BaseEnkelvoudigInformatieObjectSerializer):
    inhoud = AnyBase64File(
        view_name='enkelvoudiginformatieobjecten-download',
        help_text=_(f"Minimal accepted size of uploaded file = {settings.MIN_UPLOAD_SIZE} bytes "
                    f"(or {naturalsize(settings.MIN_UPLOAD_SIZE, binary=True)})")
    )

    def create(self):
        """
        Handle the create calls.
        """
        return drc_storage_adapter.creeer_enkelvoudiginformatieobject(self.validated_data.copy())

    def update(self, identificatie, lock):
        """
        Handle the update calls.
        """
        return drc_storage_adapter.update_enkenvoudiginformatieobject(identificatie, lock, self.validated_data.copy())


class RetrieveEnkelvoudigInformatieObjectSerializer(BaseEnkelvoudigInformatieObjectSerializer):
    # Add extra fields that are used in the return
    url = serializers.URLField(max_length=200, allow_blank=True, allow_null=True)
    inhoud = serializers.URLField(max_length=200, allow_blank=True, allow_null=True)
    bestandsomvang = serializers.IntegerField(
        read_only=True, min_value=0,
        help_text=_("Aantal bytes dat de inhoud van INFORMATIEOBJECT in beslag neemt.")
    )
    locked = serializers.BooleanField(
        label=_("locked"),
        help_text=_(
            "Geeft aan of het document gelocked is. Alleen als een document gelocked is, "
            "mogen er aanpassingen gemaakt worden."
        )
    )
    versie = serializers.IntegerField()
    beginRegistratie = serializers.DateTimeField(
        allow_null=True
    )

    def create(self):
        raise NotImplementedError('This should not be used')

    def update(self, identificatie):
        raise NotImplementedError('This should not be used')

    class Meta:
        read_only_fields = [
            'versie',
            'begin_registratie',
        ]


class PaginateSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.URLField()
    previous = serializers.URLField()
    results = RetrieveEnkelvoudigInformatieObjectSerializer(many=True, read_only=True)


class EnkelvoudigInformatieObjectWithLockSerializer(EnkelvoudigInformatieObjectSerializer):
    """
    This serializer class is used by EnkelvoudigInformatieObjectViewSet for
    update and partial_update operations
    """
    lock = serializers.CharField(
        write_only=True,
        help_text=_("Lock must be provided during updating the document (PATCH, PUT), "
                    "not while creating it"),
    )

    def validate(self, attrs):
        valid_attrs = super().validate(attrs)

        if not self.instance.canonical.lock:
            raise serializers.ValidationError(
                _("Unlocked document can't be modified"),
                code='unlocked'
            )

        try:
            lock = valid_attrs['lock']
        except KeyError:
            raise serializers.ValidationError(
                _("Lock id must be provided"),
                code='missing-lock-id'
            )

        # update
        if lock != self.instance.canonical.lock:
            raise serializers.ValidationError(
                _("Lock id is not correct"),
                code='incorrect-lock-id'
            )
        return valid_attrs


class LockEnkelvoudigInformatieObjectSerializer(serializers.ModelSerializer):
    """
    Serializer for the lock action of EnkelvoudigInformatieObjectCanonical
    model
    """
    lock = serializers.CharField(
        read_only=True,
        help_text=_("Lock must be provided during updating the document (PATCH, PUT), "
                    "not while creating it"),
    )

    def validate(self, attrs):
        valid_attrs = super().validate(attrs)
        if self.instance.lock:
            raise serializers.ValidationError(
                _("The document is already locked"),
                code='existing-lock'
            )
        return valid_attrs

    def save(self, **kwargs):
        self.instance.lock = uuid.uuid4().hex
        self.instance.save()

        return self.instance


class UnlockEnkelvoudigInformatieObjectSerializer(serializers.ModelSerializer):
    """
    Serializer for the unlock action of EnkelvoudigInformatieObjectCanonical
    model
    """
    class Meta:
        model = EnkelvoudigInformatieObjectCanonical
        fields = ('lock', )
        extra_kwargs = {
            'lock': {
                'required': False,
                'write_only': True,
            }
        }

    def validate(self, attrs):
        valid_attrs = super().validate(attrs)
        force_unlock = self.context.get('force_unlock', False)

        if force_unlock:
            return valid_attrs

        lock = valid_attrs.get('lock', '')
        if lock != self.instance.lock:
            raise serializers.ValidationError(
                _("Lock id is not correct"),
                code='incorrect-lock-id'
            )
        return valid_attrs

    def save(self, **kwargs):
        self.instance.lock = ''
        self.instance.save()
        return self.instance


class ObjectInformatieObjectSerializer(serializers.Serializer):
    url = serializers.URLField(allow_blank=True, allow_null=True, required=False)
    informatieobject = serializers.URLField(allow_blank=True, allow_null=True, validators=[IsImmutableValidator()], help_text=get_help_text('datamodel.ObjectInformatieObject', 'informatieobject'),)
    object = serializers.URLField(
        max_length=200, allow_blank=True, allow_null=True,
        validators=[URLValidator(get_auth=get_zrc_auth, headers={'Accept-Crs': 'EPSG:4326'}), IsImmutableValidator()],
        help_text="URL naar het gerelateerde OBJECT."
    )
    object_type = serializers.ChoiceField(allow_blank=True, allow_null=True, choices=ObjectTypes.choices, validators=[IsImmutableValidator()], help_text="Het type van het gerelateerde OBJECT.\n\nUitleg bij mogelijke waarden:")

    class Meta:
        extra_kwargs = {
            'url': {
                'lookup_field': 'uuid',
            },
            'informatieobject': {
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
        validators = [ObjectInformatieObjectValidator(), InformatieObjectUniqueValidator('object', 'informatieobject')]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        value_display_mapping = add_choice_values_help_text(ObjectTypes)
        self.fields['object_type'].help_text += f"\n\n{value_display_mapping}"

        if not hasattr(self, 'initial_data'):
            return

    def create(self):
        """
        Handle backend calls.
        """
        return drc_storage_adapter.creeer_objectinformatieobject(self.validated_data.copy())

    def update(self, identificatie):
        """
        Handle backend calls.
        """
        return drc_storage_adapter.update_objectinformatieobject(identificatie, self.validated_data.copy())


class GebruiksrechtenSerializer(serializers.HyperlinkedModelSerializer):
    informatieobject = serializers.URLField(
        max_length=255, required=False, allow_blank=True, allow_null=True,
    )
    #     view_name='enkelvoudiginformatieobjecten-detail',
    #     lookup_field='uuid',
    #     queryset=EnkelvoudigInformatieObject.objects,
    #     help_text=get_help_text('datamodel.Gebruiksrechten', 'informatieobject'),
    # )

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
            # 'informatieobject': {
            #     'validators': [IsImmutableValidator()],
            # },
        }
