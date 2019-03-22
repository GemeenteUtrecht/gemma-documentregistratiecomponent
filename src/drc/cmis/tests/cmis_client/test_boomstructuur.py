from time import time
from unittest import skipIf

from django.conf import settings
from django.test import TestCase

from cmislib.exceptions import ObjectNotFoundException

from .mixins import DMSMixin


@skipIf(not settings.CMIS_BACKEND_ENABLED, "Skipped if CMIS should not be active")
class CMISClientTests(DMSMixin, TestCase):
    def test_boomstructuur(self):
        """
        Test dat de boomstructuur Zaken -> Zaaktype -> Zaak gemaakt wordt.
        """
        with self.assertRaises(ObjectNotFoundException):
            self.client._repo.getObjectByPath('/Zaken')

        self.client.creeer_zaakfolder(self.zaak_url)

        # Zaken root folder
        root_folder = self.client._repo.getObjectByPath('/Zaken')

        children = [child for child in root_folder.getChildren()]
        self.assertEqual(len(children), 1)

        # zaak subfolder
        zaak_folder = children[0]
        self.assertEqual(zaak_folder.name, 'httpzaaknllocatie')
        self.assertExpectedProps(zaak_folder, {
            'cmis:objectTypeId': 'F:zsdms:zaak',
            'cmis:baseTypeId': 'cmis:folder',
            'cmis:path': '/Zaken/httpzaaknllocatie',
            'zsdms:startdatum': None,
            'zsdms:einddatum': None,
            'zsdms:zaakniveau': None,  # TODO
            'zsdms:deelzakenindicatie': None,  # TODO
            'zsdms:registratiedatum': None,
            'zsdms:archiefnominatie': None,
            'zsdms:datumVernietigDossier': None,
        })

    def test_boomstructuur_unique_name(self):
        """
        Test dat de boomstructuur Zaken -> Zaaktype -> Zaak gemaakt wordt.
        """
        with self.assertRaises(ObjectNotFoundException):
            self.client._repo.getObjectByPath('/Zaken')

        stamp = time()
        self.client.creeer_zaakfolder(stamp)

        # Zaken root folder
        root_folder = self.client._repo.getObjectByPath('/Zaken')

        children = [child for child in root_folder.getChildren()]
        self.assertEqual(len(children), 1)

        # zaak subfolder
        zaak_folder = children[0]
        self.assertEqual(zaak_folder.name, '{}'.format(stamp).replace('.', ''))
        self.assertExpectedProps(zaak_folder, {
            'cmis:objectTypeId': 'F:zsdms:zaak',
            'cmis:baseTypeId': 'cmis:folder',
            'cmis:path': '/Zaken/{}'.format(stamp).replace('.', ''),
            'zsdms:startdatum': None,
            'zsdms:einddatum': None,
            'zsdms:zaakniveau': None,  # TODO
            'zsdms:deelzakenindicatie': None,  # TODO
            'zsdms:registratiedatum': None,
            'zsdms:archiefnominatie': None,
            'zsdms:datumVernietigDossier': None,
        })
