from django.conf import settings
from django.urls import include, path

urlpatterns = []

if settings.ENABLE_CMIS:
    urlpatterns += [
        path('cmis/', include('drc_cmis.urls', namespace='cmis')),
    ]
