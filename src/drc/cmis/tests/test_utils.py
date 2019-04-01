from django.test import TestCase

from drc.cmis.utils import (
    FolderConfig, get_cmis_object_id, get_cmis_object_id_parts
)

from .mixins import DMSMixin


class UtilsTests(DMSMixin, TestCase):
    def test_get_cmis_object_id_parts(self):
        parts = get_cmis_object_id_parts('workspace://SpacesStore/76038f79-ce1e-4116-a58d-eaa619117923')
        self.assertEqual(parts, ('76038f79-ce1e-4116-a58d-eaa619117923', None, None))

    def test_get_cmis_object_id_parts_with_version(self):
        parts = get_cmis_object_id_parts('workspace://SpacesStore/76038f79-ce1e-4116-a58d-eaa619117923;v1')
        self.assertEqual(parts, ('76038f79-ce1e-4116-a58d-eaa619117923', 'v1', None))

    def test_get_cmis_object_id_parts_with_path(self):
        parts = get_cmis_object_id_parts('SpacesStore/76038f79-ce1e-4116-a58d-eaa619117923')
        self.assertEqual(parts, ('76038f79-ce1e-4116-a58d-eaa619117923', None, 'SpacesStore'))

    def test_get_cmis_object_id_parts_with_version_and_path(self):
        parts = get_cmis_object_id_parts('SpacesStore/76038f79-ce1e-4116-a58d-eaa619117923;v1')
        self.assertEqual(parts, ('76038f79-ce1e-4116-a58d-eaa619117923', 'v1', 'SpacesStore'))

    def test_get_cmis_object_id(self):
        object_id = get_cmis_object_id('workspace://SpacesStore/76038f79-ce1e-4116-a58d-eaa619117923')
        self.assertEqual(object_id, '76038f79-ce1e-4116-a58d-eaa619117923')

    def test_folder_config_no_params(self):
        with self.assertRaises(AssertionError) as exc:
            folder_config = FolderConfig()

        self.assertEqual(exc.exception.args, ('Either type or name is required', ))

    def test_folder_config_with_type(self):
        folder_config = FolderConfig(type_='test')
        self.assertEqual(folder_config.__repr__(), "<FolderConfig type_='test' name=None>")

    def test_folder_config_with_name(self):
        folder_config = FolderConfig(name='test')
        self.assertEqual(folder_config.__repr__(), "<FolderConfig type_=None name='test'>")

    def test_folder_config_with_type_and_name(self):
        folder_config = FolderConfig(type_='test', name='test')
        self.assertEqual(folder_config.__repr__(), "<FolderConfig type_='test' name='test'>")
