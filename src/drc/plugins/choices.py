from django.utils.translation import ugettext_lazy as _

from djchoices import ChoiceItem, DjangoChoices


class BackendChoices(DjangoChoices):
    django_file_storage = ChoiceItem('drc.backend.django.DjangoDRCStorageBackend', _('Django file storage'))
    cmis_file_storage = ChoiceItem('drc_cmis.backend.CMISDRCStorageBackend', _('CMIS file storage'))
