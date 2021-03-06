import uuid
from base64 import b64encode
from datetime import date

from django.test import override_settings
from django.utils import timezone

from freezegun import freeze_time
from privates.test import temp_private_root
from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.tests import (
    JWTAuthMixin, get_operation_url, get_validation_errors, reverse,
    reverse_lazy
)

from drc.backend import drc_storage_adapter
from drc.datamodel.models import (
    EnkelvoudigInformatieObject, EnkelvoudigInformatieObjectCanonical
)
from drc.datamodel.tests.factories import (
    EnkelvoudigInformatieObjectFactory, ObjectInformatieObjectFactory
)
from drc.tests.mixins import DMSMixin

INFORMATIEOBJECTTYPE = 'https://example.com/ztc/api/v1/catalogus/1/informatieobjecttype/1'


@freeze_time('2018-06-27')
@temp_private_root()
class EnkelvoudigInformatieObjectAPITests(DMSMixin, JWTAuthMixin, APITestCase):

    list_url = reverse(EnkelvoudigInformatieObject)
    heeft_alle_autorisaties = True

    @override_settings(LINK_FETCHER='vng_api_common.mocks.link_fetcher_200')
    def test_create(self):
        content = {
            'identificatie': uuid.uuid4().hex,
            'bronorganisatie': '159351741',
            'creatiedatum': '2018-06-27',
            'titel': 'detailed summary',
            'auteur': 'test_auteur',
            'formaat': 'txt',
            'taal': 'eng',
            'bestandsnaam': 'dummy.txt',
            'inhoud': b64encode(b'some file content').decode('utf-8'),
            'link': 'http://een.link',
            'beschrijving': 'test_beschrijving',
            'informatieobjecttype': INFORMATIEOBJECTTYPE,
            'vertrouwelijkheidaanduiding': 'openbaar',
        }

        # Send to the API
        response = self.client.post(self.list_url, content)

        # Test response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        # Test database
        self.assertEqual(EnkelvoudigInformatieObject.objects.count(), 1)
        stored_object = EnkelvoudigInformatieObject.objects.get()

        self.assertEqual(stored_object.identificatie, content['identificatie'])
        self.assertEqual(stored_object.bronorganisatie, '159351741')
        self.assertEqual(stored_object.creatiedatum, date(2018, 6, 27))
        self.assertEqual(stored_object.titel, 'detailed summary')
        self.assertEqual(stored_object.auteur, 'test_auteur')
        self.assertEqual(stored_object.formaat, 'txt')
        self.assertEqual(stored_object.taal, 'eng')
        self.assertEqual(stored_object.versie, 100)
        self.assertAlmostEqual(stored_object.begin_registratie, timezone.now())
        self.assertEqual(stored_object.bestandsnaam, 'dummy.txt')
        self.assertEqual(stored_object.inhoud.read(), b'some file content')
        self.assertEqual(stored_object.link, 'http://een.link')
        self.assertEqual(stored_object.beschrijving, 'test_beschrijving')
        self.assertEqual(stored_object.informatieobjecttype, INFORMATIEOBJECTTYPE)
        self.assertEqual(stored_object.vertrouwelijkheidaanduiding, 'openbaar')

        expected_url = reverse('enkelvoudiginformatieobjecten-detail', kwargs={
            'version': '1',
            'uuid': stored_object.uuid,
        })
        expected_file_url = get_operation_url('enkelvoudiginformatieobject_download', uuid=stored_object.uuid)

        expected_response = content.copy()
        expected_response.update({
            'url': f"http://testserver{expected_url}",
            'inhoud': f"{stored_object.inhoud.url}",
            'versie': 100,
            'beginRegistratie': stored_object.begin_registratie.isoformat().replace('+00:00', 'Z'),
            'vertrouwelijkheidaanduiding': 'openbaar',
            'bestandsomvang': stored_object.inhoud.size,
            'integriteit': {
                'algoritme': '',
                'waarde': '',
                'datum': None,
            },
            'ontvangstdatum': None,
            'verzenddatum': None,
            'ondertekening': {
                'soort': '',
                'datum': None,
            },
            'indicatieGebruiksrecht': None,
            'status': '',
            'locked': False,
        })

        response_data = response.json()
        self.assertEqual(sorted(response_data.keys()), sorted(expected_response.keys()))

        for key in response_data.keys():
            with self.subTest(field=key):
                self.assertEqual(response_data[key], expected_response[key])

    def test_read(self):
        test_object = EnkelvoudigInformatieObjectFactory.create(
            informatieobjecttype=INFORMATIEOBJECTTYPE,
            begin_registratie=timezone.now()
        )
        print(test_object)

        # Retrieve from the API
        detail_url = reverse('enkelvoudiginformatieobjecten-detail', kwargs={
            'version': '1',
            'uuid': test_object.uuid,
        })

        response = self.client.get(detail_url)

        # Test response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        file_url = get_operation_url('enkelvoudiginformatieobject_download', uuid=test_object.uuid)
        expected = {
            'url': f'http://localhost:8000{detail_url}',
            'identificatie': test_object.identificatie,
            'bronorganisatie': test_object.bronorganisatie,
            'creatiedatum': '2018-06-27',
            'titel': test_object.titel,
            'auteur': 'some auteur',
            'status': '',
            'formaat': 'some formaat',
            'taal': 'nld',
            'beginRegistratie': test_object.begin_registratie.isoformat().replace('+00:00', 'Z'),
            'versie': 110,
            'bestandsnaam': '',
            'inhoud': f'{test_object.inhoud}',
            'bestandsomvang': test_object.bestandsomvang,
            'link': '',
            'beschrijving': '',
            'ontvangstdatum': None,
            'verzenddatum': None,
            'ondertekening': {
                'soort': '',
                'datum': None,
            },
            'indicatieGebruiksrecht': None,
            'vertrouwelijkheidaanduiding': 'openbaar',
            'integriteit': {
                'algoritme': '',
                'waarde': '',
                'datum': None,
            },
            'informatieobjecttype': INFORMATIEOBJECTTYPE,
            'locked': False,
        }
        response_data = response.json()
        self.assertEqual(sorted(response_data.keys()), sorted(expected.keys()))

        for key in response_data.keys():
            with self.subTest(field=key):
                self.assertEqual(response_data[key], expected[key])

    def test_bestandsomvang(self):
        """
        Assert that the API shows the filesize.
        """
        test_object = EnkelvoudigInformatieObjectFactory.create(
            inhoud__data=b'some content'
        )

        # Retrieve from the API
        detail_url = reverse('enkelvoudiginformatieobjecten-detail', kwargs={
            'version': '1',
            'uuid': test_object.uuid,
        })

        response = self.client.get(detail_url)

        # Test response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bestandsomvang'], 12)  # 12 bytes

    @override_settings(LINK_FETCHER='vng_api_common.mocks.link_fetcher_200')
    def test_integrity_empty(self):
        """
        Assert that integrity is optional.
        """
        content = {
            'identificatie': uuid.uuid4().hex,
            'bronorganisatie': '159351741',
            'creatiedatum': '2018-12-13',
            'titel': 'Voorbeelddocument',
            'auteur': 'test_auteur',
            'formaat': 'text/plain',
            'taal': 'eng',
            'bestandsnaam': 'dummy.txt',
            'vertrouwelijkheidaanduiding': 'openbaar',
            'inhoud': b64encode(b'some file content').decode('utf-8'),
            'informatieobjecttype': 'https://example.com/ztc/api/v1/catalogus/1/informatieobjecttype/1',
            'integriteit': None,
        }

        # Send to the API
        response = self.client.post(self.list_url, content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        stored_object = drc_storage_adapter.lees_enkelvoudiginformatieobjecten(page=1, page_size=1, filters=None).results[0]
        self.assertEqual(stored_object.integriteit, {
            "algoritme": "",
            "waarde": "",
            "datum": None,
        })

    @override_settings(LINK_FETCHER='vng_api_common.mocks.link_fetcher_200')
    def test_integrity_provided(self):
        """
        Assert that integrity is saved.
        """
        content = {
            'identificatie': uuid.uuid4().hex,
            'bronorganisatie': '159351741',
            'creatiedatum': '2018-12-13',
            'titel': 'Voorbeelddocument',
            'auteur': 'test_auteur',
            'formaat': 'text/plain',
            'taal': 'eng',
            'bestandsnaam': 'dummy.txt',
            'vertrouwelijkheidaanduiding': 'openbaar',
            'inhoud': b64encode(b'some file content').decode('utf-8'),
            'informatieobjecttype': 'https://example.com/ztc/api/v1/catalogus/1/informatieobjecttype/1',
            'integriteit': {
                "algoritme": "md5",
                "waarde": "27c3a009a3cbba674d0b3e836f2d4685",
                "datum": "2018-12-13",
            },
        }

        # Send to the API
        response = self.client.post(self.list_url, content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        stored_object = drc_storage_adapter.lees_enkelvoudiginformatieobjecten(page=1, page_size=1, filters=None).results[0]
        self.assertEqual(stored_object.integriteit, {
            "algoritme": "md5",
            "waarde": "27c3a009a3cbba674d0b3e836f2d4685",
            "datum": date(2018, 12, 13),
        })

    def test_filter_by_identification(self):
        EnkelvoudigInformatieObjectFactory.create(identificatie='foo')
        EnkelvoudigInformatieObjectFactory.create(identificatie='bar')

        response = self.client.get(self.list_url, {'identificatie': 'foo'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()['results']

        self.assertEqual(len(response_data), 1)
        self.assertEqual(response_data[0]['identificatie'], 'foo')

    @override_settings(LINK_FETCHER='zds_schema.mocks.link_fetcher_200')
    def test_update(self):
        content = {
            'identificatie': uuid.uuid4().hex,
            'bronorganisatie': '159351741',
            'creatiedatum': '2018-06-27',
            'titel': 'detailed summary',
            'auteur': 'test_auteur',
            'formaat': 'txt',
            'taal': 'eng',
            'bestandsnaam': 'dummy.txt',
            'inhoud': b64encode(b'some file content').decode('utf-8'),
            'link': 'http://een.link',
            'beschrijving': 'test_beschrijving',
            'informatieobjecttype': 'https://example.com/ztc/api/v1/catalogus/1/informatieobjecttype/1',
            'vertrouwelijkheidaanduiding': 'openbaar',
        }

        # Send to the API
        response = self.client.post(self.list_url, content)

        # Test response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        update_content = {
            'identificatie': content.get('identificatie'),
            'bronorganisatie': '159351741',
            'creatiedatum': '2018-06-27',
            'titel': 'detailed summary',
            'auteur': 'andere_auteur',
            'formaat': 'txt',
            'taal': 'eng',
            'bestandsnaam': 'dummy.txt',
            'inhoud': b64encode(b'other content').decode('utf-8'),
            'link': 'http://een.link',
            'beschrijving': 'test_beschrijving',
            'informatieobjecttype': 'https://example.com/ztc/api/v1/catalogus/1/informatieobjecttype/1',
            'vertrouwelijkheidaanduiding': 'openbaar',
        }

        self.assertEqual(EnkelvoudigInformatieObject.objects.count(), 1)
        enkelvoudig_informatie = EnkelvoudigInformatieObject.objects.first()
        object_url = reverse_lazy('enkelvoudiginformatieobjecten-detail', kwargs={'version': '1', 'uuid': enkelvoudig_informatie.uuid})
        response = self.client.put(object_url, update_content)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

    @override_settings(LINK_FETCHER='zds_schema.mocks.link_fetcher_200')
    def test_read_response(self):
        content = {
            'identificatie': uuid.uuid4().hex,
            'bronorganisatie': '159351741',
            'creatiedatum': '2018-06-27',
            'titel': 'detailed summary',
            'auteur': 'test_auteur',
            'formaat': 'txt',
            'taal': 'eng',
            'bestandsnaam': 'dummy.txt',
            'inhoud': b64encode(b'some file content').decode('utf-8'),
            'link': 'http://een.link',
            'beschrijving': 'test_beschrijving',
            'informatieobjecttype': 'https://example.com/ztc/api/v1/catalogus/1/informatieobjecttype/1',
            'vertrouwelijkheidaanduiding': 'openbaar',
        }

        # Send to the API
        response = self.client.post(self.list_url, content)
        # Test response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(EnkelvoudigInformatieObject.objects.count(), 1)

        enkelvoudig_informatie = EnkelvoudigInformatieObject.objects.first()
        object_url = reverse_lazy('enkelvoudiginformatieobjecten-detail', kwargs={'version': '1', 'uuid': enkelvoudig_informatie.uuid})
        response = self.client.get(object_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data, {
            'url': 'http://testserver/api/v1/enkelvoudiginformatieobjecten/{}'.format(enkelvoudig_informatie.uuid),
            'identificatie': enkelvoudig_informatie.identificatie, 'bronorganisatie': '159351741',
            'creatiedatum': '2018-06-27', 'titel': 'detailed summary',
            'vertrouwelijkheidaanduiding': 'openbaar', 'auteur': 'test_auteur', 'status': '',
            'formaat': 'txt', 'taal': 'eng', 'bestandsnaam': 'dummy.txt',
            'inhoud': enkelvoudig_informatie.inhoud.url,
            # 'inhoud': 'http://testserver/cmis/content/{}'.format(enkelvoudig_informatie.uuid),
            'bestandsomvang': 17, 'link': 'http://een.link', 'beschrijving': 'test_beschrijving',
            'ontvangstdatum': None, 'verzenddatum': None, 'indicatie_gebruiksrecht': None,
            'ondertekening': {'soort': '', 'datum': None}, 'integriteit': {
                'algoritme': '', 'waarde': '', 'datum': None
            }, 'informatieobjecttype': 'https://example.com/ztc/api/v1/catalogus/1/informatieobjecttype/1'
        })

    def test_destroy_no_relations_allowed(self):
        """
        Assert that destroying is possible when there are no relations.
        """
        eio = EnkelvoudigInformatieObjectFactory.create()

        response = self.client.delete(eio.url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_destroy_with_relations_not_allowed(self):
        """
        Assert that destroying is not possible when there are relations.
        """
        eio = EnkelvoudigInformatieObjectFactory.create()
        ObjectInformatieObjectFactory.create(informatieobject=eio.canonical)
        url = reverse(eio)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, "nonFieldErrors")
        self.assertEqual(error["code"], "pending-relations")


@override_settings(LINK_FETCHER='vng_api_common.mocks.link_fetcher_200')
class EnkelvoudigInformatieObjectVersionHistoryAPITests(DMSMixin, JWTAuthMixin, APITestCase):
    list_url = reverse(EnkelvoudigInformatieObject)
    heeft_alle_autorisaties = True

    def test_eio_update(self):
        eio = EnkelvoudigInformatieObjectFactory.create(
            beschrijving='beschrijving1',
            informatieobjecttype=INFORMATIEOBJECTTYPE,
        )

        eio_response = self.client.get(eio.url)
        eio_data = eio_response.data

        lock = self.client.post(f'{eio.url}/lock').data['lock']
        eio_data.update({
            'beschrijving': 'beschrijving2',
            'inhoud': b64encode(b'aaaaa'),
            'lock': lock
        })

        for i in ['integriteit', 'ondertekening']:
            eio_data.pop(i)

        response = self.client.put(eio.url, eio_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()

        self.assertEqual(response_data['beschrijving'], 'beschrijving2')

        drc_storage_adapter.unlock_enkelvoudiginformatieobject(eio.uuid, lock)
        latest_version = drc_storage_adapter.lees_enkelvoudiginformatieobject(uuid=eio.uuid)
        self.assertEqual(latest_version.versie, 200)
        self.assertEqual(latest_version.beschrijving, 'beschrijving2')

        self.assertEqual(eio.versie, 110)
        self.assertEqual(eio.beschrijving, 'beschrijving1')

    def test_eio_partial_update(self):
        eio = EnkelvoudigInformatieObjectFactory.create(beschrijving='beschrijving1')

        eio_url = reverse('enkelvoudiginformatieobjecten-detail', kwargs={
            'uuid': eio.uuid,
        })
        lock = self.client.post(f'{eio_url}/lock').data['lock']
        response = self.client.patch(eio_url, {
            'beschrijving': 'beschrijving2',
            'lock': lock
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()

        self.assertEqual(response_data['beschrijving'], 'beschrijving2')
        drc_storage_adapter.unlock_enkelvoudiginformatieobject(eio.uuid, lock)

        latest_version = drc_storage_adapter.lees_enkelvoudiginformatieobject(uuid=eio.uuid)
        self.assertEqual(latest_version.versie, 200)
        self.assertEqual(latest_version.beschrijving, 'beschrijving2')

        self.assertEqual(eio.versie, 110)
        self.assertEqual(eio.beschrijving, 'beschrijving1')

    def test_eio_delete(self):
        eio = EnkelvoudigInformatieObjectFactory.create(beschrijving='beschrijving1')

        # lock = self.client.post(f'{eio.url}/lock').data['lock']
        # self.client.patch(eio.url, {
        #     'beschrijving': 'beschrijving2',
        #     'lock': lock
        # })

        response = self.client.delete(eio.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(EnkelvoudigInformatieObjectCanonical.objects.exists())
        self.assertFalse(EnkelvoudigInformatieObject.objects.exists())

    def test_eio_detail_retrieves_latest_version(self):
        eio = EnkelvoudigInformatieObjectFactory.create(beschrijving='beschrijving1')

        eio_url = reverse('enkelvoudiginformatieobjecten-detail', kwargs={
            'uuid': eio.uuid,
        })
        lock = self.client.post(f'{eio_url}/lock').data['lock']
        self.client.patch(eio_url, {
            'beschrijving': 'beschrijving2',
            'lock': lock
        })

        drc_storage_adapter.unlock_enkelvoudiginformatieobject(eio.uuid, lock)

        response = self.client.get(eio_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['beschrijving'], 'beschrijving2')

    def test_eio_list_shows_latest_versions(self):
        eio1 = EnkelvoudigInformatieObjectFactory(beschrijving='object1')
        eio1_url = reverse('enkelvoudiginformatieobjecten-detail', kwargs={
            'uuid': eio1.uuid,
        })
        lock = self.client.post(f'{eio1_url}/lock').data['lock']
        self.client.patch(eio1_url, {
            'beschrijving': 'object1 versie2',
            'lock': lock
        })
        eio1 = drc_storage_adapter.unlock_enkelvoudiginformatieobject(eio1.uuid, lock)

        eio2 = EnkelvoudigInformatieObjectFactory(beschrijving='object2')
        eio2_url = reverse('enkelvoudiginformatieobjecten-detail', kwargs={
            'uuid': eio2.uuid,
        })
        lock = self.client.post(f'{eio2_url}/lock').data['lock']
        self.client.patch(eio2_url, {
            'beschrijving': 'object2 versie2',
            'lock': lock
        })
        eio2 = drc_storage_adapter.unlock_enkelvoudiginformatieobject(eio2.uuid, lock)

        list_url = reverse(EnkelvoudigInformatieObject)
        print(list_url)
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        print(response.data)
        response_data = response.data['results']
        print(response_data)
        self.assertEqual(len(response_data), 2)

        self.assertEqual(response_data[0]['beschrijving'], 'object1 versie2')
        self.assertEqual(response_data[1]['beschrijving'], 'object2 versie2')

    def test_eio_detail_filter_by_version(self):
        eio = EnkelvoudigInformatieObjectFactory.create(beschrijving='beschrijving1')

        eio_url = reverse('enkelvoudiginformatieobjecten-detail', kwargs={
            'uuid': eio.uuid,
        })
        lock = self.client.post(f'{eio_url}/lock').data['lock']
        self.client.patch(eio_url, {
            'beschrijving': 'beschrijving2',
            'lock': lock
        })

        response = self.client.get(eio_url, {'versie': 100})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['beschrijving'], 'beschrijving1')

    def test_eio_detail_filter_by_wrong_version_gives_404(self):
        eio = EnkelvoudigInformatieObjectFactory.create(beschrijving='beschrijving1')
        lock = self.client.post(f'{eio.url}/lock').data['lock']
        self.client.patch(eio.url, {
            'beschrijving': 'beschrijving2',
            'lock': lock
        })

        response = self.client.get(eio.url, {'versie': 100})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_eio_detail_filter_by_registratie_op(self):
        with freeze_time('2019-01-01 12:00:00'):
            eio = EnkelvoudigInformatieObjectFactory.create(beschrijving='beschrijving1')

        eio_url = reverse('enkelvoudiginformatieobjecten-detail', kwargs={
            'uuid': eio.uuid,
        })
        lock = self.client.post(f'{eio_url}/lock').data['lock']
        with freeze_time('2019-01-01 13:00:00'):
            self.client.patch(eio_url, {
                'beschrijving': 'beschrijving2',
                'lock': lock
            })

        response = self.client.get(eio_url, {'registratieOp': '2019-01-01T12:00:00'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['beschrijving'], 'beschrijving1')

    @freeze_time('2019-01-01 12:00:00')
    def test_eio_detail_filter_by_wrong_registratie_op_gives_404(self):
        eio = EnkelvoudigInformatieObjectFactory.create(beschrijving='beschrijving1')

        lock = self.client.post(f'{eio.url}/lock').data['lock']
        self.client.patch(eio.url, {
            'beschrijving': 'beschrijving2',
            'lock': lock
        })
        response = self.client.get(eio.url, {'registratieOp': '2019-01-01T11:59:00'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, msg=response.data)

    def test_eio_download_content_filter_by_version(self):
        eio = EnkelvoudigInformatieObjectFactory.create(
            beschrijving='beschrijving1',
            inhoud__data=b'inhoud1'
        )

        lock = self.client.post(f'{eio.url}/lock').data['lock']
        self.client.patch(eio.url, {
            'inhoud': b64encode(b'inhoud2'),
            'beschrijving': 'beschrijving2',
            'lock': lock
        })

        response = self.client.get(eio.url, {'versie': 100})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(response.json())
        response = self.client.get(response.data['inhoud'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response._container[0], b'inhoud1')

    def test_eio_download_content_filter_by_registratie(self):
        with freeze_time('2019-01-01 12:00:00'):
            eio = EnkelvoudigInformatieObjectFactory.create(
                beschrijving='beschrijving1',
                inhoud__data=b'inhoud1'
            )

        eio_url = reverse('enkelvoudiginformatieobjecten-detail', kwargs={
            'uuid': eio.uuid,
        })
        lock = self.client.post(f'{eio_url}/lock').data['lock']
        with freeze_time('2019-01-01 13:00:00'):
            self.client.patch(eio_url, {
                'inhoud': b64encode(b'inhoud2'),
                'beschrijving': 'beschrijving2',
                'lock': lock
            })

        response = self.client.get(eio_url, {'registratieOp': '2019-01-01T12:00:00'})

        response = self.client.get(response.data['inhoud'])
        self.assertEqual(response._container[0], b'inhoud1')


@override_settings(LINK_FETCHER='vng_api_common.mocks.link_fetcher_200')
class EnkelvoudigInformatieObjectPaginationAPITests(DMSMixin, JWTAuthMixin, APITestCase):
    list_url = reverse(EnkelvoudigInformatieObject)
    heeft_alle_autorisaties = True

    def test_pagination_default(self):
        """
        Deleting a Besluit causes all related objects to be deleted as well.
        """
        EnkelvoudigInformatieObjectFactory.create_batch(2)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        self.assertEqual(response_data['count'], 2)
        self.assertIsNone(response_data['previous'])
        self.assertIsNone(response_data['next'])

    def test_pagination_page_param(self):
        EnkelvoudigInformatieObjectFactory.create_batch(2)

        response = self.client.get(self.list_url, {'page': 1})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        self.assertEqual(response_data['count'], 2)
        self.assertIsNone(response_data['previous'])
        self.assertIsNone(response_data['next'])
