from unittest.mock import patch

from django.test import TestCase

from drc.cmis.apps import check_cmis


class CheckCMISTests(TestCase):
    def test_check_cmis(self):
        check_cmis('test')

    # @patch('drc.cmis.client.CmisClient')
    # def test_check_cmis_no_multifilling(self, client_mock):
    #     client_mock.return_value = 2
    #     check_cmis('test')
    #     print(dir(client_mock))
    #     self.assertTrue(client_mock.called)
