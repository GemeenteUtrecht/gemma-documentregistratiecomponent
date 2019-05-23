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
    ObjectInformatieObjectSerializer,
    RetrieveEnkelvoudigInformatieObjectSerializer
)


class SerializerClassMixin:
    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_serializer_class(self):
        """
        Return the class to use for the serializer.
        Defaults to using `self.serializer_class`.

        You may want to override this if you need to provide different
        serializations depending on the incoming request.

        (Eg. admins get full serialization, others get basic serialization)
        """
        assert self.serializer_class is not None, (
            "'%s' should either include a `serializer_class` attribute, "
            "or override the `get_serializer_class()` method."
            % self.__class__.__name__
        )

        return self.serializer_class

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }


# TODO: Fix that notifications can be send.
class EnkelvoudigInformatieObjectViewSet(SerializerClassMixin, viewsets.ViewSet):
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

    def list(self, request, version=None):
        documents_data = drc_storage_adapter.get_documents()
        serializer = RetrieveEnkelvoudigInformatieObjectSerializer(data=documents_data, many=True)
        if serializer.is_valid():
            return Response(serializer.initial_data)
        assert False, serializer.errors
        return Response({"message": "invalid data"}, status=500)

    def retrieve(self, request, uuid=None, version=None):
        document_data = drc_storage_adapter.get_document(uuid=uuid)
        serializer = RetrieveEnkelvoudigInformatieObjectSerializer(data=document_data)
        if serializer.is_valid():
            return Response(serializer.initial_data)
        assert False, serializer.errors
        return Response({"message": "invalid data"}, status=500)

    def create(self, request, version=None):
        serializer = EnkelvoudigInformatieObjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.create()

        headers = self.get_success_headers(serializer.data)
        response = Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        # self.notify(response.status_code, response.data)
        return response

    def update(self, request, uuid=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update(uuid)

        headers = self.get_success_headers(serializer.data)
        response = Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        # self.notify(response.status_code, response.data)
        return response

    def partial_update(self, request, uuid=None):
        # self.notify(response.status_code, response.data)
        return response

    def destroy(self, request, uuid=None):
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
