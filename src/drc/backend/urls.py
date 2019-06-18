from django.conf import settings
from django.urls import include, path

urlpatterns = []

if settings.CMIS_ENABLED:
    urlpatterns += [
        path('cmis/', include('drc_cmis.urls', namespace="cmis")),
    ]
