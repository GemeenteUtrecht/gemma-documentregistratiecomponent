from io import BytesIO

from django.test import TestCase

from drc.cmis.storage import BinaireInhoud


class BinaureInhoudTests(TestCase):
    def test_to_cmis(self):
        inhoud = BinaireInhoud(None, 'filename')
        self.assertEqual(inhoud.to_cmis(), None)

    def test_to_cmis_with_inhoud(self):
        inhoud = BinaireInhoud(b'test', 'filename')
        self.assertEqual(inhoud.to_cmis().read(), b'test')
