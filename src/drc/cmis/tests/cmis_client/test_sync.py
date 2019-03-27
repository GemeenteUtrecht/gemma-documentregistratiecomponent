# # TODO, Test the sync function of the client
# from collections import OrderedDict
# from datetime import date, datetime
# from io import BytesIO
# from unittest import skipIf

# from django.conf import settings
# from django.test import TestCase, override_settings

# import pytz

# from drc.datamodel.tests.factories import EnkelvoudigInformatieObjectFactory

# from ...exceptions import DocumentExistsError, SyncException
# from ...models import ChangeLog
# from .mixins import DMSMixin


# @skipIf(not settings.CMIS_BACKEND_ENABLED, "Skipped if CMIS should not be active")
# class CMISClientTests(DMSMixin, TestCase):
#     def test_run_sync_dryrun(self):
#         self.client.sync(dryrun=True)

#     def test_run_sync(self):
#         result = self.client.sync()
#         self.assertEqual(result, OrderedDict([
#             ('created', 0),
#             ('updated', 0),
#             ('deleted', 0),
#             ('security', 0),
#             ('failed', 3984),
#         ]))

#     def test_run_sync_twice_at_the_same_time(self):
#         ChangeLog.objects.create(token=1)

#         with self.assertRaises(SyncException) as exc:
#             self.client.sync()

#         self.assertEqual(exc.exception.args, ('A synchronization process is already running.',))

#     def test_run_sync_twice(self):
#         result1 = self.client.sync()
#         self.assertEqual(result1, OrderedDict([
#             ('created', 0),
#             ('updated', 0),
#             ('deleted', 0),
#             ('security', 0),
#             ('failed', 3984),
#         ]))

#         result2 = self.client.sync()
#         self.assertEqual(result2, {})
