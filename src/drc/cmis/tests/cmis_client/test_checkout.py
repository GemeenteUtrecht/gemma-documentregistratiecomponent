from unittest import skipIf

from django.conf import settings
from django.test import TestCase

from cmislib.exceptions import UpdateConflictException

from drc.datamodel.tests.factories import EnkelvoudigInformatieObjectFactory

from ...exceptions import DocumentConflictException, DocumentLockedException
from ..mixins import DMSMixin


@skipIf(not settings.CMIS_BACKEND_ENABLED, "Skipped if CMIS should not be active")
class CMISClientTests(DMSMixin, TestCase):
    def test_checkout(self):
        """
        Assert that checking out a document locks it and returns the PWC ID
        """
        self.cmis_client.creeer_zaakfolder(self.zaak_url)
        document = EnkelvoudigInformatieObjectFactory.create(
            titel='testnaam', identificatie='31415926535', beschrijving='Een beschrijving'
        )
        cmis_doc = self.cmis_client.maak_zaakdocument(document, self.zaak_url)

        checkout_id, checkout_by = self.cmis_client.checkout(document)

        pwc = cmis_doc.getPrivateWorkingCopy()
        self.assertEqual(
            checkout_id,
            pwc.properties['cmis:versionSeriesCheckedOutId']
        )
        self.assertEqual(checkout_by, 'admin')

    def test_checkout_checked_out_doc(self):
        self.cmis_client.creeer_zaakfolder(self.zaak_url)
        document = EnkelvoudigInformatieObjectFactory.create(
            titel='testnaam', identificatie='31415926535', beschrijving='Een beschrijving'
        )
        cmis_doc = self.cmis_client.maak_zaakdocument(document, self.zaak_url)
        cmis_doc.checkout()

        with self.assertRaises(DocumentLockedException):
            self.cmis_client.checkout(document)

    def test_cancel_checkout(self):
        self.cmis_client.creeer_zaakfolder(self.zaak_url)
        document = EnkelvoudigInformatieObjectFactory.create(
            titel='testnaam', identificatie='31415926535', beschrijving='Een beschrijving'
        )
        self.cmis_client.maak_zaakdocument(document, self.zaak_url)
        checkout_id, _checkout_by = self.cmis_client.checkout(document)

        result = self.cmis_client.cancel_checkout(document, checkout_id)
        self.assertIsNone(result)

        # if the doc cannot be checked out, it was not unlocked
        cmis_doc = self.cmis_client._get_cmis_doc(document)
        try:
            cmis_doc.checkout()
        except UpdateConflictException:
            self.fail("Could not lock document after checkout cancel, it is still locked")

    def test_cancel_checkout_invalid_checkout_id(self):
        self.cmis_client.creeer_zaakfolder(self.zaak_url)
        document = EnkelvoudigInformatieObjectFactory.create(
            titel='testnaam', identificatie='31415926535', beschrijving='Een beschrijving'
        )
        self.cmis_client.maak_zaakdocument(document, self.zaak_url)
        _checkout_id, _checkout_by = self.cmis_client.checkout(document)

        with self.assertRaises(DocumentConflictException):
            self.cmis_client.cancel_checkout(document, '')
