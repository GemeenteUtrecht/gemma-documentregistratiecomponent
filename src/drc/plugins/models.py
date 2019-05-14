import os
import subprocess

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext

from solo.models import SingletonModel


class StorageConfig(SingletonModel):
    django_storage = models.BooleanField(default=True)
    cmis_storage = models.BooleanField(default=False)

    def __str__(self):
        return ugettext('Storage Config')

    def get_backends(self):
        backends = []

        # CMIS should be leading over django storage. For when you'll make the switch
        if self.cmis_storage:
            backends.append('drc_cmis.backend.CMISDRCStorageBackend')

        if self.django_storage:
            backends.append('drc.backend.django.DjangoDRCStorageBackend')

        return backends

    def clean(self):
        if self.cmis_storage and 'drc_cmis' not in settings.INSTALLED_APPS:
            raise ValidationError('drc_cmis staat niet aan. Daarom kan de cmis storage niet gebruikt worden.')

        if not self.django_storage and not self.cmis_storage:
            raise ValidationError('Er moet minimaal 1 storage aangevinkt zijn.')

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)

        path = os.path.join(settings.DJANGO_PROJECT_DIR, 'wsgi.py')
        subprocess.run(["touch", path])

        return instance

        # # Clear the current registry
        # site._registry = {}
        # # Reload the admin so the correct models will show up.
        # autodiscover()
