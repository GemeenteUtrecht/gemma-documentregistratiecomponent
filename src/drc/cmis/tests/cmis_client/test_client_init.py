from django.test import TestCase

from cmislib.exceptions import CmisException

from drc.cmis.client import CMISDRCClient


class TestClient(CMISDRCClient):
    def __init__(self):
        super().__init__(
            url='http://test.com/',
            user='test',
            password='test',
        )


class TestClientTests(TestCase):
    def test_init_test_client(self):
        with self.assertRaises(CmisException):
            TestClient()
