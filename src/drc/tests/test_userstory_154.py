"""
Test filtering ZaakInformatieObject on Zaak.

See:
* https://github.com/VNG-Realisatie/gemma-zaken/issues/154 (us)
* https://github.com/VNG-Realisatie/gemma-zaken/issues/239 (mapping)
"""
import uuid

from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.tests import (
    JWTAuthMixin, TypeCheckMixin, get_operation_url
)

from drc.api.scopes import SCOPE_DOCUMENTEN_ALLES_LEZEN
from drc.backend import drc_storage_adapter
from drc.datamodel.tests.factories import (
    EnkelvoudigInformatieObjectFactory, ObjectInformatieObjectFactory
)

from .mixins import DMSMixin

INFORMATIEOBJECTTYPE = 'https://example.com/ztc/api/v1/catalogus/1/informatieobjecttype/1'


class US154Tests(DMSMixin, TypeCheckMixin, JWTAuthMixin, APITestCase):

    scopes = [SCOPE_DOCUMENTEN_ALLES_LEZEN]
    informatieobjecttype = INFORMATIEOBJECTTYPE

    def test_informatieobjecttype_filter(self):
        zaak_url = 'http://www.example.com/zrc/api/v1/zaken/1'

        eio1 = EnkelvoudigInformatieObjectFactory()
        oio1 = drc_storage_adapter.creeer_objectinformatieobject({
            'uuid': uuid.uuid4(),
            'informatieobject': eio1.url, 'object': zaak_url, 'object_type': 'zaak'
        })

        eio2 = EnkelvoudigInformatieObjectFactory()
        oio2 = drc_storage_adapter.creeer_objectinformatieobject({
            'uuid': uuid.uuid4(),
            'informatieobject': eio2.url, 'object': zaak_url, 'object_type': 'zaak'
        })

        eio3 = EnkelvoudigInformatieObjectFactory()
        oio3 = drc_storage_adapter.creeer_objectinformatieobject({
            'uuid': uuid.uuid4(),
            'informatieobject': eio3.url, 'object': 'http://www.example.com/zrc/api/v1/zaken/2', 'object_type': 'zaak'
        })

        url = get_operation_url('objectinformatieobject_list')

        response = self.client.get(url, {'object': zaak_url})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())

        response_data = response.json()
        self.assertEqual(len(response_data), 2)

        for zio in response_data:
            self.assertEqual(zio['object'], zaak_url)
