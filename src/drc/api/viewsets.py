from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from sendfile import sendfile
from vng_api_common.audittrails.viewsets import (
    AuditTrailCreateMixin, AuditTrailDestroyMixin, AuditTrailViewSet,
    AuditTrailViewsetMixin
)
from vng_api_common.notifications.viewsets import (
    NotificationCreateMixin, NotificationViewSetMixin
)
from vng_api_common.serializers import FoutSerializer

from drc.datamodel.models import (
    EnkelvoudigInformatieObject, Gebruiksrechten, ObjectInformatieObject
)

from .audits import AUDIT_DRC
from .data_filtering import ListFilterByAuthorizationsMixin
from .filters import (
    EnkelvoudigInformatieObjectFilter, GebruiksrechtenFilter,
    ObjectInformatieObjectFilter
)
from .kanalen import KANAAL_DOCUMENTEN
from .permissions import (
    InformationObjectAuthScopesRequired,
    InformationObjectRelatedAuthScopesRequired
)
from .scopes import (
    SCOPE_DOCUMENTEN_AANMAKEN, SCOPE_DOCUMENTEN_ALLES_LEZEN,
    SCOPE_DOCUMENTEN_ALLES_VERWIJDEREN, SCOPE_DOCUMENTEN_BIJWERKEN,
    SCOPE_DOCUMENTEN_GEFORCEERD_UNLOCK, SCOPE_DOCUMENTEN_LOCK
)
from .serializers import (
    EnkelvoudigInformatieObjectSerializer, GebruiksrechtenSerializer,
    LockEnkelvoudigInformatieObjectSerializer,
    ObjectInformatieObjectSerializer,
    UnlockEnkelvoudigInformatieObjectSerializer
)


class EnkelvoudigInformatieObjectViewSet(NotificationViewSetMixin,
                                         ListFilterByAuthorizationsMixin,
                                         AuditTrailViewsetMixin,
                                         viewsets.ModelViewSet):
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
    queryset = EnkelvoudigInformatieObject.objects.all()
    serializer_class = EnkelvoudigInformatieObjectSerializer
    filterset_class = EnkelvoudigInformatieObjectFilter
    lookup_field = 'uuid'
    permission_classes = (InformationObjectAuthScopesRequired, )
    required_scopes = {
        'list': SCOPE_DOCUMENTEN_ALLES_LEZEN,
        'retrieve': SCOPE_DOCUMENTEN_ALLES_LEZEN,
        'create': SCOPE_DOCUMENTEN_AANMAKEN,
        'destroy': SCOPE_DOCUMENTEN_ALLES_VERWIJDEREN,
        'update': SCOPE_DOCUMENTEN_BIJWERKEN,
        'partial_update': SCOPE_DOCUMENTEN_BIJWERKEN,
        'download': SCOPE_DOCUMENTEN_ALLES_LEZEN,
        'lock': SCOPE_DOCUMENTEN_LOCK,
        'unlock': SCOPE_DOCUMENTEN_LOCK | SCOPE_DOCUMENTEN_GEFORCEERD_UNLOCK
    }
    notifications_kanaal = KANAAL_DOCUMENTEN
    audit = AUDIT_DRC

    @swagger_auto_schema(
        method='get',
        # see https://swagger.io/docs/specification/2-0/describing-responses/ and
        # https://swagger.io/docs/specification/2-0/mime-types/
        # OAS 3 has a better mechanism: https://swagger.io/docs/specification/describing-responses/
        produces=["application/octet-stream"],
        responses={
            status.HTTP_200_OK: openapi.Response(
                "De binaire bestandsinhoud",
                schema=openapi.Schema(type=openapi.TYPE_FILE)
            ),
            status.HTTP_401_UNAUTHORIZED: openapi.Response("Unauthorized", schema=FoutSerializer),
            status.HTTP_403_FORBIDDEN: openapi.Response("Forbidden", schema=FoutSerializer),
            status.HTTP_404_NOT_FOUND: openapi.Response("Not found", schema=FoutSerializer),
            status.HTTP_406_NOT_ACCEPTABLE: openapi.Response("Not acceptable", schema=FoutSerializer),
            status.HTTP_410_GONE: openapi.Response("Gone", schema=FoutSerializer),
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: openapi.Response("Unsupported media type", schema=FoutSerializer),
            status.HTTP_429_TOO_MANY_REQUESTS: openapi.Response("Throttled", schema=FoutSerializer),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response("Internal server error", schema=FoutSerializer),
        }
    )
    @action(methods=['get'], detail=True)
    def download(self, request, *args, **kwargs):
        eio = self.get_object()
        return sendfile(
            request,
            eio.inhoud.path,
            attachment=True,
            mimetype='application/octet-stream'
        )

    @swagger_auto_schema(
        request_body=LockEnkelvoudigInformatieObjectSerializer,
        responses={
            status.HTTP_200_OK: LockEnkelvoudigInformatieObjectSerializer,
            status.HTTP_400_BAD_REQUEST: openapi.Response("Bad request", schema=FoutSerializer),
            status.HTTP_401_UNAUTHORIZED: openapi.Response("Unauthorized", schema=FoutSerializer),
            status.HTTP_403_FORBIDDEN: openapi.Response("Forbidden", schema=FoutSerializer),
            status.HTTP_404_NOT_FOUND: openapi.Response("Not found", schema=FoutSerializer),
            status.HTTP_406_NOT_ACCEPTABLE: openapi.Response("Not acceptable", schema=FoutSerializer),
            status.HTTP_410_GONE: openapi.Response("Gone", schema=FoutSerializer),
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: openapi.Response("Unsupported media type", schema=FoutSerializer),
            status.HTTP_429_TOO_MANY_REQUESTS: openapi.Response("Throttled", schema=FoutSerializer),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response("Internal server error", schema=FoutSerializer),
        }
    )
    @action(detail=True, methods=['post'])
    def lock(self, request, *args, **kwargs):
        eio = self.get_object()
        lock_serializer = LockEnkelvoudigInformatieObjectSerializer(eio, data=request.data)
        lock_serializer.is_valid(raise_exception=True)
        lock_serializer.save()
        return Response(lock_serializer.data)

    @swagger_auto_schema(
        request_body=UnlockEnkelvoudigInformatieObjectSerializer,
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response("No content"),
            status.HTTP_400_BAD_REQUEST: openapi.Response("Bad request", schema=FoutSerializer),
            status.HTTP_401_UNAUTHORIZED: openapi.Response("Unauthorized", schema=FoutSerializer),
            status.HTTP_403_FORBIDDEN: openapi.Response("Forbidden", schema=FoutSerializer),
            status.HTTP_404_NOT_FOUND: openapi.Response("Not found", schema=FoutSerializer),
            status.HTTP_406_NOT_ACCEPTABLE: openapi.Response("Not acceptable", schema=FoutSerializer),
            status.HTTP_410_GONE: openapi.Response("Gone", schema=FoutSerializer),
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: openapi.Response("Unsupported media type", schema=FoutSerializer),
            status.HTTP_429_TOO_MANY_REQUESTS: openapi.Response("Throttled", schema=FoutSerializer),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response("Internal server error", schema=FoutSerializer),
        }
    )
    @action(detail=True, methods=['post'])
    def unlock(self, request, *args, **kwargs):
        eio = self.get_object()
        # check if it's a force unlock by administrator
        force_unlock = False
        if self.request.jwt_auth.has_auth(
            scopes=SCOPE_DOCUMENTEN_GEFORCEERD_UNLOCK,
            informatieobjecttype=eio.informatieobjecttype,
            vertrouwelijkheidaanduiding=eio.vertrouwelijkheidaanduiding
        ):
            force_unlock = True

        unlock_serializer = UnlockEnkelvoudigInformatieObjectSerializer(
            eio,
            data=request.data,
            context={'force_unlock': force_unlock}
        )
        unlock_serializer.is_valid(raise_exception=True)
        unlock_serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ObjectInformatieObjectViewSet(NotificationCreateMixin,
                                    AuditTrailCreateMixin,
                                    AuditTrailDestroyMixin,
                                    ListFilterByAuthorizationsMixin,
                                    mixins.CreateModelMixin,
                                    mixins.DestroyModelMixin,
                                    viewsets.ReadOnlyModelViewSet):
    """
    Opvragen en bewerken van Object-Informatieobject relaties.

    create:
    OPGELET: dit endpoint hoor je als client NIET zelf aan te spreken.

    ZRC en BRC gebruiken deze endpoint bij het synchroniseren van relaties.

    Registreer welk(e) INFORMATIEOBJECT(en) een OBJECT kent.

    **Er wordt gevalideerd op**
    - geldigheid informatieobject URL
    - uniek zijn van relatie OBJECT-INFORMATIEOBJECT
    - bestaan van relatie OBJECT-INFORMATIEOBJECT in het ZRC of DRC (waar het
      object leeft)

    list:
    Geef een lijst van relaties tussen OBJECTen en INFORMATIEOBJECTen.

    retrieve:
    Geef een informatieobject terug wat gekoppeld is aan het huidige object

    destroy:
    Verwijder een relatie tussen een object en een informatieobject
    """
    queryset = ObjectInformatieObject.objects.all()
    serializer_class = ObjectInformatieObjectSerializer
    filterset_class = ObjectInformatieObjectFilter
    lookup_field = 'uuid'
    notifications_kanaal = KANAAL_DOCUMENTEN
    notifications_main_resource_key = 'informatieobject'
    permission_classes = (InformationObjectRelatedAuthScopesRequired,)
    required_scopes = {
        'list': SCOPE_DOCUMENTEN_ALLES_LEZEN,
        'retrieve': SCOPE_DOCUMENTEN_ALLES_LEZEN,
        'create': SCOPE_DOCUMENTEN_AANMAKEN,
        'destroy': SCOPE_DOCUMENTEN_ALLES_VERWIJDEREN,
        'update': SCOPE_DOCUMENTEN_BIJWERKEN,
        'partial_update': SCOPE_DOCUMENTEN_BIJWERKEN,
    }
    audit = AUDIT_DRC
    audittrail_main_resource_key = 'informatieobject'


class GebruiksrechtenViewSet(NotificationViewSetMixin,
                             ListFilterByAuthorizationsMixin,
                             AuditTrailViewsetMixin,
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
    permission_classes = (InformationObjectRelatedAuthScopesRequired,)
    required_scopes = {
        'list': SCOPE_DOCUMENTEN_ALLES_LEZEN,
        'retrieve': SCOPE_DOCUMENTEN_ALLES_LEZEN,
        'create': SCOPE_DOCUMENTEN_AANMAKEN,
        'destroy': SCOPE_DOCUMENTEN_ALLES_VERWIJDEREN,
        'update': SCOPE_DOCUMENTEN_BIJWERKEN,
        'partial_update': SCOPE_DOCUMENTEN_BIJWERKEN,
    }
    audit = AUDIT_DRC
    audittrail_main_resource_key = 'informatieobject'


class EnkelvoudigInformatieObjectAuditTrailViewSet(AuditTrailViewSet):
    """
    Opvragen van Audit trails horend bij een EnkelvoudigInformatieObject.

    list:
    Geef een lijst van AUDITTRAILS die horen bij het huidige EnkelvoudigInformatieObject.

    retrieve:
    Haal de details van een AUDITTRAIL op.
    """
    main_resource_lookup_field = 'enkelvoudiginformatieobject_uuid'
