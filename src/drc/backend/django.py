from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from import_class import import_class


class DjangoDRCStorageBackend(import_class(settings.ABSTRACT_BASE_CLASS)):
    """
    This is the backend that is used to store the documents in a CMIS compatible backend.
    """
    def create_document(self, data, content):
        from drc.datamodel.models import EnkelvoudigInformatieObject
        eio = EnkelvoudigInformatieObject.objects.create(inhoud=content, **data)
        return eio

    def get_documents(self, filters=None):
        # TODO: Implement the filter options
        from drc.datamodel.models import EnkelvoudigInformatieObject
        return EnkelvoudigInformatieObject.objects.all()

    def get_document(self, identification):
        from drc.datamodel.models import EnkelvoudigInformatieObject
        try:
            return EnkelvoudigInformatieObject.objects.get(identificatie=identification)
        except ObjectDoesNotExist:
            raise self.exception_class(_('Het enkelvoudiginformatieobject kan niet worden gevonden.'))

    def update_document(self, identification, data, content):
        from drc.datamodel.models import EnkelvoudigInformatieObject
        try:
            eio = EnkelvoudigInformatieObject.objects.get(identificatie=identification)
        except ObjectDoesNotExist:
            raise self.exception_class(_('Het enkelvoudiginformatieobject kan niet worden gevonden.'))
        else:
            # TODO: Implement the update action
            eio.save()
            return eio

    def delete_document(self, identification):
        from drc.datamodel.models import EnkelvoudigInformatieObject
        try:
            eio = EnkelvoudigInformatieObject.objects.get(identificatie=identification)
        except ObjectDoesNotExist:
            raise self.exception_class(_('Het enkelvoudiginformatieobject kan niet worden gevonden.'))
        else:
            eio.delete()

    def create_document_case_connection(self, data):
        from drc.datamodel.models import ObjectInformatieObject, EnkelvoudigInformatieObject
        informatieobject = data.pop("informatieobject")
        uuid = informatieobject.split('/')[-1]
        eio = EnkelvoudigInformatieObject.objects.get(uuid=uuid)
        oio = ObjectInformatieObject.objects.create(informatieobject=eio, **data)
        return oio

    def get_document_case_connections(self):
        from drc.datamodel.models import ObjectInformatieObject
        return ObjectInformatieObject.objects.all()

    def get_document_case_connection(self, identification):
        from drc.datamodel.models import ObjectInformatieObject
        try:
            return ObjectInformatieObject.objects.get(uuid=identification)
        except ObjectDoesNotExist:
            raise self.exception_class(_('Het object informatieobject kan niet worden gevonden.'))

    def update_document_case_connection(self, identification, data):
        from drc.datamodel.models import ObjectInformatieObject
        try:
            oio = ObjectInformatieObject.objects.get(uuid=identification)
        except ObjectDoesNotExist:
            raise self.exception_class(_('Het object informatieobject kan niet worden gevonden.'))
        else:
            # TODO: Implement the update action
            oio.save()
            return oio

    def delete_document_case_connection(self, identification):
        from drc.datamodel.models import ObjectInformatieObject
        try:
            oio = ObjectInformatieObject.objects.get(uuid=identification)
        except ObjectDoesNotExist:
            raise self.exception_class(_('Het object informatieobject kan niet worden gevonden.'))
        else:
            oio.delete()
