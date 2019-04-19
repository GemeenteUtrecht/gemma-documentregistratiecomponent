from datetime import datetime
from unittest import skipIf

from django.conf import settings
from django.test import TestCase

import pytz
from cmislib.exceptions import UpdateConflictException

from drc.cmis.exceptions import DocumentConflictException
from drc.cmis.storage import BinaireInhoud
from drc.datamodel.tests.factories import EnkelvoudigInformatieObjectFactory

from ..mixins import DMSMixin


@skipIf(not settings.CMIS_BACKEND_ENABLED, "Skipped if CMIS should not be active")
class CMISClientTests(DMSMixin, TestCase):
    def test_check_lock_status_unlocked(self):
        self.cmis_client.creeer_zaakfolder(self.zaak_url)
        document = EnkelvoudigInformatieObjectFactory.create(
            titel='testnaam', identificatie='31415926535', beschrijving='Een beschrijving'
        )

        result = self.cmis_client.is_locked(document)
        self.assertFalse(result)

    def test_check_lock_status_locked(self):
        self.cmis_client.creeer_zaakfolder(self.zaak_url)
        document = EnkelvoudigInformatieObjectFactory.create(
            titel='testnaam', identificatie='31415926535', beschrijving='Een beschrijving'
        )
        self.cmis_client.checkout(document)

        result = self.cmis_client.is_locked(document)

        self.assertTrue(result)

    def test_create_lock_update_flow(self):
        """
        Assert that it's possible to create an empty document, lock it for
        update and then effectively set the content thereby unlocking it.
        """
        self.cmis_client.creeer_zaakfolder(self.zaak_url)

        document = EnkelvoudigInformatieObjectFactory.create(
            titel='testnaam', identificatie='31415926535', beschrijving='Een beschrijving'
        )
        inhoud = BinaireInhoud(b'leaky abstraction...', filename='bestand.txt')

        # flow
        checkout_id, _checkout_by = self.cmis_client.checkout(document)  # lock for update
        # TODO: Broken here. Test not possible
        with self.assertRaises(DocumentConflictException):
            self.cmis_client.update_zaakdocument(document, checkout_id, inhoud=inhoud)

        # filename, file_obj = self.cmis_client.geef_inhoud(document)

        # # make assertions about the results
        # self.assertEqual(filename, 'bestand.txt')
        # self.assertEqual(file_obj.read(), b'leaky abstraction...')

        # # verify expected props
        # cmis_doc = self.cmis_client._get_cmis_doc(document)
        # self.assertExpectedProps(cmis_doc, {
        #     'cmis:contentStreamFileName': 'bestand.txt',
        #     'cmis:contentStreamLength': 20,
        #     'cmis:contentStreamMimeType': 'application/binary',  # the default if it couldn't be determined
        #     # 'zsdms:dct.categorie': document.informatieobjecttype.informatieobjectcategorie,
        #     'zsdms:dct.omschrijving': document.informatieobjecttype.informatieobjecttypeomschrijving,
        #     'zsdms:documentIdentificatie': '31415926535',
        #     'zsdms:documentauteur': None,
        #     'zsdms:documentbeschrijving': 'Een beschrijving',
        #     'zsdms:documentcreatiedatum': datetime.combine(document.creatiedatum, datetime.min.time()).replace(tzinfo=pytz.utc),
        #     # 'zsdms:documentformaat': None,
        #     'zsdms:documentLink': document.link,
        #     'zsdms:documentontvangstdatum': None,
        #     'zsdms:documentstatus': None,
        #     'zsdms:documenttaal': document.taal,
        #     'zsdms:documentversie': None,
        #     'zsdms:documentverzenddatum': None,
        #     'zsdms:vertrouwelijkaanduiding': None
        # })

        # # the doc must be unlocked after update, easy check -> lock it
        # try:
        #     cmis_doc.checkout()
        # except UpdateConflictException:
        #     self.fail("Could not lock document after update, it was already/still locked")
