from drc_cmis.client import CMISDRCClient


class DMSMixin:
    def setUp(self):
        super().setUp()
        self.cmis_client = CMISDRCClient()
        self._removeTree()
        self.cmis_client._base_folder = None

    def _removeTree(self):
        base_folder = self.cmis_client._get_base_folder
        base_folder.delete_tree()
