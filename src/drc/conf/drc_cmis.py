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
DRC_CMIS_UPLOAD_TO = os.getenv('DRC_CMIS_UPLOAD_TO', 'drc_cmis.utils.upload_to')
DRC_CMIS_CLIENT_CLASS = os.getenv('DRC_CMIS_CLIENT_CLASS', 'drc_cmis.client.CMISDRCClient')
