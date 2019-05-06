import os

#
# CMIS settings
#
DRC_STORAGE_BACKENDS = os.getenv('DRC_STORAGE_BACKENDS', ['drc.backend.django.DjangoDRCStorageBackend'])

DRC_STORAGE_BACKENDS = [
    'drc.backend.django.DjangoDRCStorageBackend',
    'drc_cmis.backend.CMISDRCStorageBackend'
]

#
# DRC_CMIS_CLIENT
#
DRC_CMIS_CLIENT_URL = os.getenv('DRC_CMIS_CLIENT_URL', 'http://localhost:8082/alfresco/cmisatom')
DRC_CMIS_CLIENT_USER = os.getenv('DRC_CMIS_CLIENT_USER', 'admin')
DRC_CMIS_CLIENT_USER_PASSWORD = os.getenv('DRC_CMIS_CLIENT_USER_PASSWORD', 'admin')
