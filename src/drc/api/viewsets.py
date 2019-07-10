import logging

from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.settings import api_settings
from vng_api_common.notifications.viewsets import NotificationViewSetMixin
from vng_api_common.permissions import ActionScopesRequired

from drc.backend import drc_storage_adapter
from drc.datamodel.models import (
    EnkelvoudigInformatieObject, Gebruiksrechten, ObjectInformatieObject
)
from drc.sync.signals import oio_change

from .filters import (
    EnkelvoudigInformatieObjectFilter, GebruiksrechtenFilter,
    ObjectInformatieObjectFilter
)
from .kanalen import KANAAL_DOCUMENTEN
from .notifications import NotificationMixin
from .scopes import SCOPE_DOCUMENTEN_ALLES_VERWIJDEREN
from .serializers import (
    EnkelvoudigInformatieObjectSerializer, GebruiksrechtenSerializer,
    ObjectInformatieObjectSerializer,
    RetrieveEnkelvoudigInformatieObjectSerializer
)

logger = logging.getLogger(__name__)


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


class EnkelvoudigInformatieObjectViewSet(SerializerClassMixin, NotificationMixin, viewsets.ViewSet):
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
    lookup_url_kwarg = 'uuid'
    permission_classes = (ActionScopesRequired, )
    required_scopes = {
        'destroy': SCOPE_DOCUMENTEN_ALLES_VERWIJDEREN,
    }
    notifications_kanaal = KANAAL_DOCUMENTEN
    notifications_resource = 'enkelvoudiginformatieobject'
    notifications_model = EnkelvoudigInformatieObject

    def list(self, request, version=None):
        filters = self.filterset_class(data=self.request.GET)
        if not filters.is_valid():
            return Response(filters.errors, status=400)

        documents_data = drc_storage_adapter.lees_enkelvoudiginformatieobjecten(filters=filters.form.cleaned_data)
        serializer = RetrieveEnkelvoudigInformatieObjectSerializer(instance=documents_data, many=True)
        return Response(serializer.data)

    def get_object(self, **kwargs):
        document_data = drc_storage_adapter.lees_enkelvoudiginformatieobject(kwargs.get('uuid'))
        return document_data

    def retrieve(self, request, uuid=None, version=None):
        serializer = RetrieveEnkelvoudigInformatieObjectSerializer(instance=self.get_object(uuid=uuid))
        return Response(serializer.data)

    def create(self, request, version=None):
        serializer = EnkelvoudigInformatieObjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.create()

        return_serializer = RetrieveEnkelvoudigInformatieObjectSerializer(instance=data)
        headers = self.get_success_headers(return_serializer.data)
        response = Response(return_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        self.notify(response.status_code, data)
        return response

    def update(self, request, uuid=None, version=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.update(uuid)

        return_serializer = RetrieveEnkelvoudigInformatieObjectSerializer(instance=data)
        headers = self.get_success_headers(return_serializer.data)
        response = Response(return_serializer.data, status=status.HTTP_200_OK, headers=headers)
        self.notify(response.status_code, data)
        return response

    def partial_update(self, request, uuid=None, version=None):
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        data = serializer.update(uuid)

        return_serializer = RetrieveEnkelvoudigInformatieObjectSerializer(instance=data)
        headers = self.get_success_headers(return_serializer.data)
        response = Response(return_serializer.data, status=status.HTTP_200_OK, headers=headers)
        self.notify(response.status_code, data)
        return response

    def destroy(self, request, uuid=None, version=None):
        data = drc_storage_adapter.verwijder_enkelvoudiginformatieobject(uuid)
        response = Response(status=status.HTTP_204_NO_CONTENT)
        self.notify(response.status_code, data)
        return response

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}


class ObjectInformatieObjectViewSet(SerializerClassMixin, NotificationMixin, viewsets.ViewSet):
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
    serializer_class = ObjectInformatieObjectSerializer
    filterset_class = ObjectInformatieObjectFilter # TODO
    lookup_field = 'uuid'

    notifications_kanaal = KANAAL_DOCUMENTEN
    notifications_resource = 'informatieobject'
    notifications_model = ObjectInformatieObject
    notifications_main_resource_key = 'informatieobject'

    def list(self, request, version=None):
        documents_data = drc_storage_adapter.lees_objectinformatieobjecten()
        serializer = ObjectInformatieObjectSerializer(instance=documents_data, many=True)
        return Response(serializer.data)

    def retrieve(self, request, uuid=None, version=None):
        document_data = drc_storage_adapter.lees_objectinformatieobject(uuid)
        serializer = ObjectInformatieObjectSerializer(instance=document_data)
        return Response(serializer.data)

    def create(self, request, version=None):
        serializer = ObjectInformatieObjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        oio = serializer.create()

        headers = self.get_success_headers(serializer.data)
        response = Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        oio_change.send(sender=self.__class__, instance=oio)
        self.notify(response.status_code, oio)
        return response

    # TODO
    def update(self, request, uuid=None, version=None):
        print(request.data)
        serializer = ObjectInformatieObjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        logger.error(dict(serializer.errors))
        oio = serializer.update(uuid)

        headers = self.get_success_headers(serializer.data)
        response = Response(serializer.data, status=status.HTTP_200_OK, headers=headers)
        oio_change.send(sender=self.__class__, instance=oio)
        self.notify(response.status_code, oio)
        return response

    # TODO
    def partial_update(self, request, uuid=None, version=None):
        logger.error(request.data)
        serializer = ObjectInformatieObjectSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            assert False, serializer.errors
        logger.error(dir(serializer))
        logger.error(serializer.data)
        logger.error(serializer.validated_data)
        oio = serializer.update(uuid)

        headers = self.get_success_headers(serializer.data)
        response = Response(serializer.data, status=status.HTTP_200_OK, headers=headers)
        oio_change.send(sender=self.__class__, instance=oio)
        self.notify(response.status_code, oio)
        return response

    def destroy(self, request, uuid=None, version=None):
        oio = drc_storage_adapter.verwijder_objectinformatieobject(uuid)
        response = Response({}, status=status.HTTP_204_NO_CONTENT)
        self.notify(response.status_code, oio)
        return response

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}


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
