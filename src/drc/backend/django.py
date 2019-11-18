import logging

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger(__name__)


class DjangoDRCStorageBackend(import_string(settings.ABSTRACT_BASE_CLASS)):
    """
    This is the backend that is used to store the documents in a CMIS compatible backend.
    """
    def create_document(self, data, content):
        from drc.datamodel.models import EnkelvoudigInformatieObject
        eio = EnkelvoudigInformatieObject.objects.create(inhoud=content, **data)
        return eio

    def get_documents(self, filters=None):
        from drc.datamodel.models import EnkelvoudigInformatieObject
        queryset = EnkelvoudigInformatieObject.objects.all()
        for key, value in filters.items():
            if value is not None and value != '':
                logger.warning('Apply filter {}: {}'.format(key, value))
                queryset = queryset.filter(**{key: value})
        return queryset

    def get_document(self, identification):
        from drc.datamodel.models import EnkelvoudigInformatieObject
        try:
            return EnkelvoudigInformatieObject.objects.get(uuid=identification)
        except ObjectDoesNotExist:
            raise self.exception_class({None: _('Het enkelvoudiginformatieobject kan niet worden gevonden.')}, retreive_single=True)

    def update_document(self, identification, data, content):
        from drc.datamodel.models import EnkelvoudigInformatieObject
        try:
            eio = EnkelvoudigInformatieObject.objects.get(uuid=identification)
        except ObjectDoesNotExist:
            raise self.exception_class({None: _('Het enkelvoudiginformatieobject kan niet worden gevonden.')}, update=True)
        else:
            for key, value in data.items():
                setattr(eio, key, value)
            eio.save()
            return eio

    def delete_document(self, identification):
        from drc.datamodel.models import EnkelvoudigInformatieObject
        try:
            eio = EnkelvoudigInformatieObject.objects.get(uuid=identification)
        except ObjectDoesNotExist:
            raise self.exception_class({None: _('Het enkelvoudiginformatieobject kan niet worden gevonden.')}, delete=True)
        else:
            eio.delete()
            return eio

    def create_document_case_connection(self, data):
        from drc.datamodel.models import ObjectInformatieObject, EnkelvoudigInformatieObject
        informatieobject = data.pop("informatieobject")
        uuid = informatieobject.split('/')[-1]
        eio = EnkelvoudigInformatieObject.objects.get(uuid=uuid)
        oio = ObjectInformatieObject.objects.create(informatieobject=eio, **data)
        return oio

    def get_document_case_connections(self, filters=None):
        from drc.datamodel.models import ObjectInformatieObject
        return ObjectInformatieObject.objects.all()

    def get_document_case_connection(self, identification):
        from drc.datamodel.models import ObjectInformatieObject
        try:
            return ObjectInformatieObject.objects.get(uuid=identification)
        except ObjectDoesNotExist:
            raise self.exception_class({None: _('Het object informatieobject kan niet worden gevonden.')}, retreive_single=True)

    def update_document_case_connection(self, identification, data):
        from drc.datamodel.models import ObjectInformatieObject, EnkelvoudigInformatieObject
        try:
            oio = ObjectInformatieObject.objects.get(uuid=identification)
        except ObjectDoesNotExist:
            raise self.exception_class({None: _('Het object informatieobject kan niet worden gevonden.')}, update=True)
        else:
            informatieobject = None
            if "informatieobject" in data:
                informatieobject = data.pop('informatieobject')

            if informatieobject:
                uuid = informatieobject.split('/')[-1]
                eio = EnkelvoudigInformatieObject.objects.get(uuid=uuid)
                oio.informatieobject = eio

            for key, value in data.items():
                setattr(oio, key, value)
            oio.save()
            return oio

    def delete_document_case_connection(self, identification):
        from drc.datamodel.models import ObjectInformatieObject
        try:
            oio = ObjectInformatieObject.objects.get(uuid=identification)
        except ObjectDoesNotExist:
            raise self.exception_class({None: _('Het object informatieobject kan niet worden gevonden.')}, delete=True)
        else:
            oio.delete()
            return oio
