from unittest import skipIf

from django.conf import settings
from django.test import TestCase

from drc.cmis.abstract import DRCClient


@skipIf(not settings.CMIS_BACKEND_ENABLED, "Skipped if CMIS should not be active")
class CMISClientTests(TestCase):
    def setUp(self):
        self.client = DRCClient()

    def test_creeer_zaakfolder(self):
        with self.assertRaises(NotImplementedError):
            self.client.creeer_zaakfolder('zaak_url')

    def test_maak_zaakdocument(self):
        with self.assertRaises(NotImplementedError):
            self.client.maak_zaakdocument('document')

    def test_maak_zaakdocument_met_inhoud(self):
        with self.assertRaises(NotImplementedError):
            self.client.maak_zaakdocument_met_inhoud('document')

    def test_geef_inhoud(self):
        with self.assertRaises(NotImplementedError):
            self.client.geef_inhoud('document')

    def test_zet_inhoud(self):
        with self.assertRaises(NotImplementedError):
            self.client.zet_inhoud('document', 'stream')

    def test_relateer_aan_zaak(self):
        with self.assertRaises(NotImplementedError):
            self.client.relateer_aan_zaak('document', 'zaak_url')

    def test_update_zaakdocument(self):
        with self.assertRaises(NotImplementedError):
            self.client.update_zaakdocument('document')

    def test_checkout(self):
        with self.assertRaises(NotImplementedError):
            self.client.checkout('document')

    def test_cancel_checkout(self):
        with self.assertRaises(NotImplementedError):
            self.client.cancel_checkout('document', 'checkout_id')

    def test_ontkoppel_zaakdocument(self):
        with self.assertRaises(NotImplementedError):
            self.client.ontkoppel_zaakdocument('document', 'zaak_url')

    def test_is_locked(self):
        with self.assertRaises(NotImplementedError):
            self.client.is_locked('document')

    def test_verwijder_document(self):
        with self.assertRaises(NotImplementedError):
            self.client.verwijder_document('document')

    def test_sync(self):
        with self.assertRaises(NotImplementedError):
            self.client.sync()
