from django.conf import settings

from cmislib.exceptions import ObjectNotFoundException

from drc.cmis.client import default_client


class DMSMixin:
    def setUp(self):
        super().setUp()

        if settings.CMIS_BACKEND_ENABLED:
            self.cmis_client = default_client
            self.addCleanup(lambda: self._removeTree('/Zaken'))
            self.addCleanup(lambda: self._removeTree('/Sites/archief/documentLibrary'))
            self.addCleanup(lambda: self._removeTree('/_temp'))
            self.addCleanup(lambda: self._removeTree('/Unfiled'))

            self.zaak_url = 'http://zaak.nl/locatie'

    def _removeTree(self, path):
        try:
            root_folder = self.cmis_client._repo.getObjectByPath(path)
        except ObjectNotFoundException:
            return
        root_folder.deleteTree()

    def assertExpectedProps(self, obj, expected: dict):
        for prop, expected_value in expected.items():
            with self.subTest(prop=prop, expected_value=expected_value):
                self.assertEqual(obj.properties[prop], expected_value, msg="prop: {}".format(prop))
