from django.test import TestCase

from drc.cmis.models import CMISMixin


class ModelTests(TestCase):
    def test_get_cmis_properties(self):
        test = CMISMixin()
        self.assertEqual(test.get_cmis_properties(), {})

    def test_get_cmis_properties_with_mapping(self):
        test = CMISMixin()
        test.test = 'test_value'
        test.CMIS_MAPPING = {'anders': 'test'}
        self.assertEqual(test.get_cmis_properties(), {'anders': 'test_value'})

    def test_get_cmis_properties_with_none_values(self):
        test = CMISMixin()
        test.test = None
        test.CMIS_MAPPING = {'anders': 'test'}
        self.assertEqual(test.get_cmis_properties(), {'anders': None})

    def test_get_cmis_properties_with_none_values_allow_none_false(self):
        test = CMISMixin()
        test.test = None
        test.CMIS_MAPPING = {'anders': 'test'}
        self.assertEqual(test.get_cmis_properties(allow_none=False), {'anders': ''})

    def test_update_cmis_properties(self):
        test = CMISMixin()
        with self.assertRaises(NotImplementedError):
            test.update_cmis_properties({})
