import uuid
from unittest.mock import patch

from django.conf import settings
from django.test import override_settings

from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.constants import ObjectTypes
from vng_api_common.tests import JWTAuthMixin, get_validation_errors, reverse
from zds_client.tests.mocks import mock_client

from drc.backend import drc_storage_adapter
from drc.datamodel.models import ObjectInformatieObject
from drc.datamodel.tests.factories import (
    EnkelvoudigInformatieObjectFactory, ObjectInformatieObjectFactory
)
from drc.tests.mixins import DMSMixin

ZAAK = 'https://zrc.nl/api/v1/zaken/1234'
BESLUIT = 'https://brc.nl/api/v1/besluiten/4321'


@override_settings(
    LINK_FETCHER='vng_api_common.mocks.link_fetcher_200',
    ZDS_CLIENT_CLASS='vng_api_common.mocks.MockClient',
    ALLOWD_HOSTS=["testserver.nl"]
)
class ObjectInformatieObjectTests(DMSMixin, JWTAuthMixin, APITestCase):
    heeft_alle_autorisaties = True

    list_url = reverse(ObjectInformatieObject)

    def test_create_with_objecttype_zaak(self):
        eio = EnkelvoudigInformatieObjectFactory.create()

        data = {
            'object': ZAAK,
            'informatieobject': eio.url,
            'objectType': 'zaak'
        }
        response = self.client.post(self.list_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response.json())

        oio = response.json()
        self.assertEqual(oio.get("object"), ZAAK)

    def test_create_with_objecttype_besluit(self):
        eio = EnkelvoudigInformatieObjectFactory.create()

        response = self.client.post(self.list_url, {
            'object': BESLUIT,
            'informatieobject': eio.url,
            'objectType': 'besluit'
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response.json())

        oio = response.json()
        self.assertEqual(oio.get("object"), BESLUIT)

    def test_duplicate_object(self):
        """
        Test the (informatieobject, object) unique together validation.
        """
        eio = EnkelvoudigInformatieObjectFactory()
        oio = drc_storage_adapter.creeer_objectinformatieobject({
            'uuid': uuid.uuid4(),
            'informatieobject': eio.url, 'object': 'https://zrc.nl/api/v1/zaken/2', 'object_type': 'zaak'
        })

        content = {
            'informatieobject': eio.url,
            'object': oio.object,
            'objectType': ObjectTypes.zaak,
        }

        # Send to the API
        response = self.client.post(self.list_url, content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
        error = get_validation_errors(response, 'nonFieldErrors')
        self.assertEqual(error['code'], 'unique')

    def test_filter(self):
        eio = EnkelvoudigInformatieObjectFactory()
        drc_storage_adapter.creeer_objectinformatieobject({
            'uuid': uuid.uuid4(),
            'informatieobject': eio.url, 'object': 'https://zrc.nl/api/v1/zaken/2', 'object_type': 'zaak'
        })
        print(self.list_url)
        response = self.client.get(self.list_url, {
            'informatieobject': eio.url,
        })
        self.assertEqual(response.status_code, 200, msg=response.json())
        self.assertEqual(len(response.data), 1)
        print(response.data)
        self.assertEqual(response.data[0]['informatieobject'], eio.url)


@patch('zds_client.client.get_operation_url')
@patch('zds_client.tests.mocks.MockClient.fetch_schema', return_value={})
class ObjectInformatieObjectDestroyTests(DMSMixin, JWTAuthMixin, APITestCase):
    heeft_alle_autorisaties = True

    RESPONSES = {
        "https://zrc.nl/api/v1/zaakinformatieobjecten": [],
        "https://brc.nl/api/v1/besluitinformatieobjecten": [{
            "url": f"https://brc.nl/api/v1/besluitinformatieobjecten/{uuid.uuid4()}",
            "informatieobject": f"http://testserver/api/v1/enkelvoudiginformatieobjecten/{uuid.uuid4()}",
            "besluit": BESLUIT,
            "aardRelatieWeergave": "Legt vast, omgekeerd: is vastgelegd in",
        }],
    }

    def test_destroy_oio_remote_gone(self, mock_fetch_schema, mock_get_operation_url):
        mock_get_operation_url.return_value = '/api/v1/zaakinformatieobjecten'
        eio = EnkelvoudigInformatieObjectFactory()
        oio = drc_storage_adapter.creeer_objectinformatieobject({
            'uuid': uuid.uuid4(),
            'informatieobject': eio.url, 'object': 'https://zrc.nl/api/v1/zaak/2', 'object_type': 'zaak'
        })

        with mock_client(responses=self.RESPONSES):
            response = self.client.delete(oio.url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, msg=response.data)
        self.assertFalse(drc_storage_adapter.lees_objectinformatieobjecten())

    def test_destroy_oio_remote_still_present(self, mock_fetch_schema, mock_get_operation_url):
        mock_get_operation_url.return_value = '/api/v1/besluitinformatieobjecten'
        eio = EnkelvoudigInformatieObjectFactory()
        oio = drc_storage_adapter.creeer_objectinformatieobject({
            'uuid': uuid.uuid4(),
            'informatieobject': eio.url, 'object': 'https://brc.nl/api/v1/besluiten/2', 'object_type': 'besluit'
        })

        with mock_client(responses=self.RESPONSES):
            response = self.client.delete(oio.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, msg=response.data)
        error = get_validation_errors(response, "nonFieldErrors")
        self.assertEqual(error["code"], "remote-relation-exists")
