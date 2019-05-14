from django.urls import include, path

from .models import StorageConfig

config = StorageConfig.get_solo()


urlpatterns = []

if config.cmis_storage:
    urlpatterns += [
        path('cmis/', include('drc_cmis.urls', namespace='cmis')),
    ]
