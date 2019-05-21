from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.settings import api_settings
from vng_api_common.notifications.viewsets import NotificationViewSetMixin
from vng_api_common.permissions import ActionScopesRequired
from vng_api_common.serializers import ValidatieFoutSerializer
from vng_api_common.viewsets import CheckQueryParamsMixin

from drc.backend import drc_storage_adapter
from drc.datamodel.models import (
    EnkelvoudigInformatieObject, Gebruiksrechten, ObjectInformatieObject
)

from .filters import (
    EnkelvoudigInformatieObjectFilter, GebruiksrechtenFilter,
    ObjectInformatieObjectFilter
)
from .kanalen import KANAAL_DOCUMENTEN
from .scopes import SCOPE_DOCUMENTEN_ALLES_VERWIJDEREN
from .serializers import (
    EnkelvoudigInformatieObjectSerializer, GebruiksrechtenSerializer,
    ObjectInformatieObjectSerializer
)


# TODO: Fix that notifications can be send.
class EnkelvoudigInformatieObjectViewSet(viewsets.ViewSet):
    """
    Ontsluit ENKELVOUDIG INFORMATIEOBJECTen.

    create:
    Registreer een ENKELVOUDIG INFORMATIEOBJECT.

    **Er wordt gevalideerd op**
    - geldigheid informatieobjecttype URL

    list:
    Geef een lijst van ENKELVOUDIGe INFORMATIEOBJECTen (=documenten).

    De objecten bevatten metadata over de documenten en de downloadlink naar
    de binary data.

    retrieve:
    Geef de details van een ENKELVOUDIG INFORMATIEOBJECT.

    Het object bevat metadata over het informatieobject en de downloadlink naar
    de binary data.

    update:
    Werk een ENKELVOUDIG INFORMATIEOBJECT bij door de volledige resource mee
    te sturen.

    **Er wordt gevalideerd op**
    - geldigheid informatieobjecttype URL

    *TODO*
    - valideer immutable attributes

    partial_update:
    Werk een ENKELVOUDIG INFORMATIEOBJECT bij door enkel de gewijzigde velden
    mee te sturen.

    **Er wordt gevalideerd op**
    - geldigheid informatieobjecttype URL

    *TODO*
    - valideer immutable attributes

    destroy:
    Verwijdert een ENKELVOUDIG INFORMATIEOBJECT, samen met alle gerelateerde
    resources binnen deze API.

    **Gerelateerde resources**
    - `ObjectInformatieObject` - alle relaties van het informatieobject
    - `Gebruiksrechten` - alle gebruiksrechten van het informatieobject
    """
    serializer_class = EnkelvoudigInformatieObjectSerializer
    filterset_class = EnkelvoudigInformatieObjectFilter
    lookup_field = 'uuid'
    permission_classes = (ActionScopesRequired, )
    required_scopes = {
        'destroy': SCOPE_DOCUMENTEN_ALLES_VERWIJDEREN,
    }
    notifications_kanaal = KANAAL_DOCUMENTEN

    @swagger_auto_schema(responses={
        200: EnkelvoudigInformatieObjectSerializer(many=True), 400: ValidatieFoutSerializer, 401: ValidatieFoutSerializer,
        403: ValidatieFoutSerializer, 406: ValidatieFoutSerializer, 409: ValidatieFoutSerializer,
        410: ValidatieFoutSerializer, 415: ValidatieFoutSerializer, 429: ValidatieFoutSerializer,
        500: ValidatieFoutSerializer,
    })
    def list(self, request, *args, **kwargs):
        documents_data = drc_storage_adapter.get_documents()

        serializer = EnkelvoudigInformatieObjectSerializer(data=documents_data, many=True)
        if serializer.is_valid():
            print(serializer.data)
            return Response(serializer.data)
        print(serializer.errors)
        return Response(data="Could not parse the data", status=500)

    @swagger_auto_schema(responses={
        200: EnkelvoudigInformatieObjectSerializer, 400: ValidatieFoutSerializer, 401: ValidatieFoutSerializer,
        403: ValidatieFoutSerializer, 406: ValidatieFoutSerializer, 409: ValidatieFoutSerializer,
        410: ValidatieFoutSerializer, 415: ValidatieFoutSerializer, 429: ValidatieFoutSerializer,
        500: ValidatieFoutSerializer,
    })
    def retrieve(self, request, pk=None):
        serializer = EnkelvoudigInformatieObjectSerializer(data={})
        return Response(serializer.data)

    @swagger_auto_schema(request_body=EnkelvoudigInformatieObjectSerializer)
    def create(self, request):
        serializer = EnkelvoudigInformatieObjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.create()

        headers = self.get_success_headers(serializer.data)
        response = Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        # self.notify(response.status_code, response.data)
        return response

    @swagger_auto_schema(request_body=EnkelvoudigInformatieObjectSerializer)
    def update(self, request, pk=None):
        serializer = EnkelvoudigInformatieObjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update(pk)

        headers = self.get_success_headers(serializer.data)
        response = Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        # self.notify(response.status_code, response.data)
        return response

    @swagger_auto_schema(request_body=EnkelvoudigInformatieObjectSerializer)
    def partial_update(self, request, pk=None):
        # self.notify(response.status_code, response.data)
        return response

    @swagger_auto_schema()
    def destroy(self, request, pk=None):
        # get data via serializer
        instance = self.get_object()
        data = self.get_serializer(instance).data
        # self.notify(response.status_code, data, instance=instance)
        return response

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}


class ObjectInformatieObjectViewSet(NotificationViewSetMixin,
                                    CheckQueryParamsMixin,
                                    viewsets.ModelViewSet):
    """
    Beheer relatie tussen InformatieObject en OBJECT.

    create:
    Registreer een INFORMATIEOBJECT bij een OBJECT. Er worden twee types van
    relaties met andere objecten gerealiseerd:

    * INFORMATIEOBJECT behoort bij [OBJECT] en
    * INFORMATIEOBJECT is vastlegging van [OBJECT].

    **Er wordt gevalideerd op**
    - geldigheid informatieobject URL
    - geldigheid object URL
    - de combinatie informatieobject en object moet uniek zijn

    **Opmerkingen**
    - De registratiedatum wordt door het systeem op 'NU' gezet. De `aardRelatie`
      wordt ook door het systeem gezet.
    - Bij het aanmaken wordt ook in de bron van het OBJECT de gespiegelde
      relatie aangemaakt, echter zonder de relatie-informatie.
    - Titel, beschrijving en registratiedatum zijn enkel relevant als het om een
      object van het type ZAAK gaat (aard relatie "hoort bij").

    list:
    Geef een lijst van relaties tussen INFORMATIEOBJECTen en andere OBJECTen.

    Deze lijst kan gefilterd wordt met querystringparameters.

    retrieve:
    Geef de details van een relatie tussen een INFORMATIEOBJECT en een ander
    OBJECT.

    update:
    Update een INFORMATIEOBJECT bij een OBJECT. Je mag enkel de gegevens
    van de relatie bewerken, en niet de relatie zelf aanpassen.

    **Er wordt gevalideerd op**
    - informatieobject URL, object URL en objectType mogen niet veranderen

    Titel, beschrijving en registratiedatum zijn enkel relevant als het om een
    object van het type ZAAK gaat (aard relatie "hoort bij").

    partial_update:
    Update een INFORMATIEOBJECT bij een OBJECT. Je mag enkel de gegevens
    van de relatie bewerken, en niet de relatie zelf aanpassen.

    **Er wordt gevalideerd op**
    - informatieobject URL, object URL en objectType mogen niet veranderen

    Titel, beschrijving en registratiedatum zijn enkel relevant als het om een
    object van het type ZAAK gaat (aard relatie "hoort bij").

    destroy:
    Verwijdert de relatie tussen OBJECT en INFORMATIEOBJECT.
    """
    queryset = ObjectInformatieObject.objects.all()
    serializer_class = ObjectInformatieObjectSerializer
    filterset_class = ObjectInformatieObjectFilter
    lookup_field = 'uuid'
    notifications_kanaal = KANAAL_DOCUMENTEN
    notifications_main_resource_key = 'informatieobject'


class GebruiksrechtenViewSet(NotificationViewSetMixin,
                             viewsets.ModelViewSet):
    """
    list:
    Geef een lijst van gebruiksrechten horend bij informatieobjecten.

    Er kan gefiltered worden met querystringparameters.

    retrieve:
    Haal de details op van een gebruiksrecht van een informatieobject.

    create:
    Voeg gebruiksrechten toe voor een informatieobject.

    **Opmerkingen**
    - Het toevoegen van gebruiksrechten zorgt ervoor dat de
      `indicatieGebruiksrecht` op het informatieobject op `true` gezet wordt.

    update:
    Werk een gebruiksrecht van een informatieobject bij.

    partial_update:
    Werk een gebruiksrecht van een informatieobject bij.

    destroy:
    Verwijder een gebruiksrecht van een informatieobject.

    **Opmerkingen**
    - Indien het laatste gebruiksrecht van een informatieobject verwijderd wordt,
      dan wordt de `indicatieGebruiksrecht` van het informatieobject op `null`
      gezet.
    """
    queryset = Gebruiksrechten.objects.all()
    serializer_class = GebruiksrechtenSerializer
    filterset_class = GebruiksrechtenFilter
    lookup_field = 'uuid'
    notifications_kanaal = KANAAL_DOCUMENTEN
    notifications_main_resource_key = 'informatieobject'
