from time import time
from unittest import skipIf

from django.conf import settings
from django.test import TestCase

from cmislib.exceptions import ObjectNotFoundException

from drc.cmis.choices import CMISObjectType
from drc.cmis.utils import FolderConfig

from .mixins import DMSMixin


@skipIf(not settings.CMIS_BACKEND_ENABLED, "Skipped if CMIS should not be active")
class CMISClientTests(DMSMixin, TestCase):
    def test_get_or_create_folder(self):
        """
        """
        with self.assertRaises(ObjectNotFoundException):
            self.client._repo.getObjectByPath('/Zaken')

        stamp = '{}'.format(time()).replace('.', '')
        self.client.creeer_zaakfolder(stamp)

        # Zaken root folder
        root_folder = self.client._repo.getObjectByPath('/Zaken')

        children = [child for child in root_folder.getChildren()]
        self.assertEqual(len(children), 1)

        self.client.creeer_zaakfolder(stamp)
        children = [child for child in root_folder.getChildren()]
        self.assertEqual(len(children), 1)

        self.client.creeer_zaakfolder('other')
        children = [child for child in root_folder.getChildren()]
        self.assertEqual(len(children), 2)

    def test_get_folder_name_with_name(self):
        with self.assertRaises(ObjectNotFoundException):
            self.client._repo.getObjectByPath('/Zaken')

        stamp = '{}'.format(time()).replace('.', '')
        self.client.creeer_zaakfolder(stamp)

        name = self.client.get_folder_name(stamp, FolderConfig(type_=CMISObjectType.zaken, name='test'))
        self.assertEqual(name, 'test')

    def test_get_folder_name_zaak_folder(self):
        with self.assertRaises(ObjectNotFoundException):
            self.client._repo.getObjectByPath('/Zaken')

        stamp = '{}'.format(time()).replace('.', '')
        self.client.creeer_zaakfolder(stamp)

        name = self.client.get_folder_name(stamp, FolderConfig(type_=CMISObjectType.zaak_folder))
        self.assertEqual(name, stamp)

    def test_get_folder_name_no_name(self):
        with self.assertRaises(ObjectNotFoundException):
            self.client._repo.getObjectByPath('/Zaken')

        stamp = '{}'.format(time()).replace('.', '')
        self.client.creeer_zaakfolder(stamp)

        with self.assertRaises(ValueError):
            self.client.get_folder_name(stamp, FolderConfig(type_=CMISObjectType.zaken))
