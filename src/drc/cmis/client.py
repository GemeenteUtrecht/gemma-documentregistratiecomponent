import logging
from collections import OrderedDict
from io import BytesIO

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import transaction
from django.utils.functional import LazyObject
from django.utils.module_loading import import_string
from django.utils.text import slugify

from cmislib import CmisClient
from cmislib.exceptions import ObjectNotFoundException, UpdateConflictException

from .abstract import DRCClient
from .choices import ChangeLogStatus, CMISChangeType, CMISObjectType
from .exceptions import (
    DocumentConflictException, DocumentDoesNotExistError, DocumentExistsError,
    DocumentLockedException, SyncException
)
from .models import ChangeLog
from .query import CMISQuery
from .utils import get_cmis_object_id

logger = logging.getLogger(__name__)


class CMISDRCClient(DRCClient):
    """
    DRC client implementation using the CMIS protocol.
    """
    document_query = CMISQuery("SELECT * FROM zsdms:document WHERE zsdms:documentIdentificatie = '%s'")

    def __init__(self, url=None, user=None, password=None):
        """
        Connect to the CMIS repository and store the root folder for further
        operations.

        :param url: string, CMIS provider url.
        :param user: string, username to login on the document store
        :param password: string, password to login on the document store
        """
        if url is None:
            url = settings.CMIS_CLIENT_URL
        if user is None:
            user = settings.CMIS_CLIENT_USER
        if password is None:
            password = settings.CMIS_CLIENT_USER_PASSWORD
        _client = CmisClient(url, user, password)
        self._repo = _client.getDefaultRepository()
        self._root_folder = self._repo.getObjectByPath('/')
        self.upload_to = import_string(settings.CMIS_UPLOAD_TO)

    def _get_or_create_folder(self, name, properties=None, parent=None):
        """
        Get or create the folder with :param:`name` in :param:`parent`.

        :param name: string, the name of the folder to create.
        :param properties: dictionary with cmis and/or custom properties to
          pass to the folder object
        :param parent: parent folder to create the folder in as subfolder.
          Defaults to the root folder
        :return: a tuple of (folder, boolean) where the folder is the retrieved or created folder, and
          the boolean indicates whether the folder was created or not.
        """
        if parent is None:
            parent = self._root_folder
        existing = next((child for child in parent.getChildren() if child.name == name), None)
        if existing is not None:
            return (existing, False)
        return (parent.createFolder(name, properties=properties or {}), True)

    def get_folder_name(self, zaak_url, folder_config):
        name = ''
        if folder_config.type == CMISObjectType.zaak_folder:
            name = slugify(zaak_url)
        else:
            if not folder_config.name:
                raise ValueError(('Could not determine a folder name for zaak {}').format(slugify(zaak_url)))
        return folder_config.name or name

    def _get_zaakfolder(self, zaak_url):
        upload_to = self.upload_to(zaak_url)
        bits = [self.get_folder_name(zaak_url, folder_config) for folder_config in upload_to]
        path = '/' + ('/').join(bits)
        return self._repo.getObjectByPath(path)

    def _get_cmis_doc(self, document, checkout_id=None):
        """
        Given a document instance, retrieve the underlying AtomPubDocument object.

        :param document: :class:`InformatieObject` instance.
        :return: :class:`AtomPubDocument` object
        """
        query = self.document_query(document.identificatie)
        result_set = self._repo.query(query)
        unpacked_result_set = [item for item in result_set]
        if not unpacked_result_set:
            raise DocumentDoesNotExistError(('Document met identificatie {} bestaat niet in het DRC').format(document.identificatie))
        doc = unpacked_result_set[0]
        doc = doc.getLatestVersion()
        if checkout_id is not None:
            pwc = doc.getPrivateWorkingCopy()
            if not pwc or not pwc.properties['cmis:versionSeriesCheckedOutId'] == checkout_id:
                raise DocumentConflictException("Foutieve 'pwc id' meegestuurd")
        return doc

    def _build_cmis_doc_properties(self, document, filename=None):
        properties = document.get_cmis_properties()
        properties['cmis:objectTypeId'] = CMISObjectType.edc
        if filename is not None:
            properties['cmis:name'] = filename
        return properties

    def creeer_zaakfolder(self, zaak_url):
        """
        Maak de zaak folder aan in het DRC.

        :param zaak_url: Een link naar de zaak.
        :return: :class:`cmslib.atompub_binding.AtomPubFolder` object - de
          cmslib representatie van de (aangemaakte) zaakmap.
        """
        upload_to = self.upload_to(zaak_url)
        # if not settings.CMIS_ZAKEN_TYPE_ENABLED:
        for folder_config in upload_to:
            if folder_config.type == CMISObjectType.zaken:
                folder_config.type = 'cmis:folder'

        parent = None
        for folder_config in upload_to:
            properties = {'cmis:objectTypeId': folder_config.type} if folder_config.type else {}
            name = self.get_folder_name(zaak_url, folder_config)
            parent, _ = self._get_or_create_folder(name, properties, parent=parent)

        zaak_folder = parent
        return zaak_folder

    def maak_zaakdocument(self, document, zaak_url=None, filename=None, sender=None):
        """
        4.3.5.3: Maak een EDC object aan zonder binaire inhoud.

        Het ZRC zorgt ervoor dat in het DRC een EDC-object wordt aangemaakt zonder binaire inhoud.
        Hiervoor maakt het ZRC gebruik van de CMIS-services die aangeboden worden door het DRC. Hierbij
        gelden de volgende eisen:
        - Er wordt een object aangemaakt van het objecttype EDC (Zie 5.1);
        - Het EDC-object wordt gerelateerd aan de juiste Zaakfolder (Zie 5.1);
        - Tenminste de minimaal vereiste metadata voor een EDC wordt vastgelegd in de daarvoor
        gedefinieerde objectproperties. In Tabel 3 is een mapping aangegeven tussen de StUF-ZKN-
        elementen en CMIS-objectproperties.

        :param zaak: Zaak url naar het zaak object
        :param document: EnkelvoudigInformatieObject instantie die de
          meta-informatie van het document bevat
        :param filename: Bestandsnaam van het aan te maken document.
        :param sender: De afzender.

        :return: AtomPubDocument instance die aangemaakt werd.
        :raises: DocumentExistsError wanneer er al een document met dezelfde
            identificatie bestaat, binnen de zaakfolder.
        """
        return self.maak_zaakdocument_met_inhoud(document, zaak_url, filename, sender)

    def maak_zaakdocument_met_inhoud(self, document, zaak_url=None, filename=None, sender=None, stream=None, content_type=None):
        """
        :param zaak_url: TODO
        :param document: EnkelvoudigInformatieObject instantie die de
          meta-informatie van het document bevat
        :param filename: Bestandsnaam van het aan te maken document.
        :param sender: De afzender.
        :param stream: Inhoud van het document.
        :param content_type: Aanduiding van het document type.

        :return: AtomPubDocument instance die aangemaakt werd.
        :raises: DocumentExistsError wanneer er al een document met dezelfde
            identificatie bestaat, binnen de zaakfolder.
        """
        try:
            self._get_cmis_doc(document)
        except DocumentDoesNotExistError:
            pass
        else:
            raise DocumentExistsError(('Document identificatie {} is niet uniek').format(document.identificatie))

        if stream is None:
            stream = BytesIO()
        if zaak_url is None:
            zaakfolder, _ = self._get_or_create_folder(self.TEMP_FOLDER_NAME)
        else:
            zaakfolder = self._get_zaakfolder(zaak_url)

        properties = self._build_cmis_doc_properties(document, filename=filename)
        if settings.CMIS_SENDER_PROPERTY:
            properties[settings.CMIS_SENDER_PROPERTY] = sender

        _doc = self._repo.createDocument(
            name=document.titel, properties=properties, contentFile=stream,
            contentType=content_type, parentFolder=zaakfolder
        )
        document._object_id = _doc.getObjectId().rsplit(';')[0]
        document.save(update_fields=['_object_id'])
        return _doc

    def geef_inhoud(self, document):
        """
        Retrieve the document via its identifier from the DRC.

        :param document: EnkelvoudigInformatieObject instance
        :return: tuple of (filename, BytesIO()) with the stream filename and the binary content
        """
        try:
            doc = self._get_cmis_doc(document)
        except DocumentDoesNotExistError:
            return (None, BytesIO())

        filename = doc.properties['cmis:name']
        empty = doc.properties['cmis:contentStreamId'] is None
        if empty:
            return (filename, BytesIO())
        return (filename, doc.getContentStream())

    def zet_inhoud(self, document, stream, content_type=None, checkout_id=None):
        """
        Calls setContentStream to fill the contents of an existing document. This will update the
        version of the document in the DRC.

        :param document: EnkelvoudigInformatieObject instance
        :param stream: Inhoud van het document.
        :param content_type: Aanduiding van het document type.
        :param checkout_id:
        """
        cmis_doc = self._get_cmis_doc(document, checkout_id=checkout_id)
        cmis_doc if not checkout_id else cmis_doc.getPrivateWorkingCopy()
        cmis_doc.setContentStream(stream, content_type)

    def update_zaakdocument(self, document, checkout_id=None, inhoud=None):
        cmis_doc = self._get_cmis_doc(document, checkout_id=checkout_id)
        cmis_doc if not checkout_id else cmis_doc.getPrivateWorkingCopy()
        current_properties = cmis_doc.properties
        new_properties = self._build_cmis_doc_properties(document, filename=inhoud.bestandsnaam if inhoud else None)
        diff_properties = {key: value for key, value in new_properties.items() if current_properties.get(key) != new_properties.get(key)}
        try:
            cmis_doc.updateProperties(diff_properties)
        except UpdateConflictException as exc:
            raise DocumentConflictException from exc

        if inhoud is not None:
            content = inhoud.to_cmis()
            self.zet_inhoud(document, content, None, checkout_id=checkout_id)
        if checkout_id:
            cmis_doc.checkin()

    def relateer_aan_zaak(self, document, zaak_url):
        """
        Wijs het document aan :param:`zaak` toe.

        Verplaatst het document van de huidige folder naar de zaakfolder.
        """
        cmis_doc = self._get_cmis_doc(document)
        zaakfolder = self._get_zaakfolder(zaak_url)
        parent = [parent for parent in cmis_doc.getObjectParents()][0]
        cmis_doc.move(parent, zaakfolder)

    def checkout(self, document):
        """
        Checkout (lock) the requested document and return the PWC ID + check out username.

        :param document: :class:`EnkelvoudigInformatieObject` instance.
        """
        cmis_doc = self._get_cmis_doc(document)
        try:
            pwc = cmis_doc.checkout()
        except UpdateConflictException as exc:
            raise DocumentLockedException('Document was already checked out') from exc

        pwc.reload()
        checkout_id = pwc.properties['cmis:versionSeriesCheckedOutId']
        checkout_by = pwc.properties['cmis:versionSeriesCheckedOutBy']
        return (checkout_id, checkout_by)

    def cancel_checkout(self, document, checkout_id):
        cmis_doc = self._get_cmis_doc(document, checkout_id=checkout_id)
        cmis_doc.cancelCheckout()

    def ontkoppel_zaakdocument(self, document, zaak_url):
        cmis_doc = self._get_cmis_doc(document)
        cmis_folder = self._get_zaakfolder(zaak_url)
        trash_folder, _ = self._get_or_create_folder(self.TRASH_FOLDER)
        cmis_doc.move(cmis_folder, trash_folder)

    def is_locked(self, document):
        cmis_doc = self._get_cmis_doc(document)
        pwc = cmis_doc.getPrivateWorkingCopy()
        return pwc is not None

    def verwijder_document(self, document):
        cmis_doc = self._get_cmis_doc(document)
        cmis_doc.delete()

    @transaction.atomic
    def sync(self, dryrun=False):
        """
        De zaakdocument registratie in het DRC wordt gesynchroniseerd met het
        ZRC door gebruik te maken van de CMIS-changelog. Het ZRC vraagt deze op
        bij het DRC door gebruik te maken van de CMISservice
        getContentChanges(), die het DRC biedt. Het ZRC dient door middel van de
        latestChangeLogToken te bepalen welke wijzigingen in de CMIS-changelog
        nog niet zijn verwerkt in het ZRC. Indien er wijzigingen zijn die nog
        niet zijn verwerkt in het ZRC dienen deze alsnog door het ZRC verwerkt te
        worden.

        Zie: ZDS 1.2, paragraaf 4.4

        De sync-functie, realiseert ook "Koppel Zaakdocument aan Zaak":

        Een reeds bestaand document wordt relevant voor een lopende zaak.

        De "Koppel Zaakdocument aan Zaak"-service biedt de mogelijkheid aan
        DSC's om een "los" document achteraf aan een zaak te koppelen waardoor
        het een zaakgerelateerd document wordt. Het betreft hier documenten
        die reeds bestonden en in het DRC waren vastgelegd voordat een ZAAK is
        ontstaan.

        Een document wordt binnen het DRC gekoppeld aan een lopende zaak door
        het document te relateren aan een Zaakfolder-object.

        Zie: ZDS 1.2, paragraaf 5.4.2

        :param dryrun: Retrieves all content changes from the DRC but doesn't
                       update the ZRC.
        :return: A `OrderedDict` with all `CMISChangeType`s as key and the
                 number of actions as value.
        """
        from drc.datamodel.models import EnkelvoudigInformatieObject
        self._repo.reload()
        try:
            dms_change_log_token = int(self._repo.info['latestChangeLogToken'])
        except KeyError:
            raise ImproperlyConfigured('Could not retrieve the latest change log token from the DRC.')

        if not dryrun:
            change_log = ChangeLog.objects.create(token=dms_change_log_token)
            if ((ChangeLog.objects.exclude(pk=change_log.pk)).filter(status=ChangeLogStatus.in_progress)).count() > 0:
                change_log.delete()
                raise SyncException('A synchronization process is already running.')
            else:
                pass
                # change_log = None
            last_change_log = (ChangeLog.objects.filter(status=ChangeLogStatus.completed)).last()
            last_zs_change_log_token = last_change_log.token if last_change_log else 0
            max_items = dms_change_log_token - last_zs_change_log_token
            if max_items < 0:
                raise SyncException('The DRC change log token is older than our records.')
            else:
                if max_items == 0:
                    return {}
                created, updated, deleted, security, failed = (0, 0, 0, 0, 0)
                cache = set()
                result_set = self._repo.getContentChanges(changeLogToken=last_zs_change_log_token,
                  includeProperties=True,
                  maxItems=max_items)
                for change_entry in result_set:
                    change_type = change_entry.changeType
                    object_id = get_cmis_object_id(change_entry.objectId)
                    cache_key = ('{}-{}').format(object_id, change_type)
                    if cache_key in cache:
                        continue
                    cache.add(cache_key)
                    try:
                        if change_type in [CMISChangeType.created, CMISChangeType.updated]:
                            try:
                                dms_document = self._repo.getObject(object_id)
                            except ObjectNotFoundException as e:
                                logger.error('[%s-%s] Object was %s but could not be found in the DRC.', change_entry.id, object_id, change_type)
                                failed += 1
                                continue

                            dms_object_type = dms_document.properties.get('cmis:objectTypeId')
                            if dms_object_type == CMISObjectType.edc:
                                if change_type == CMISChangeType.updated:
                                    try:
                                        zs_document_id = dms_document.properties.get('zsdms:documentIdentificatie')
                                        edc = EnkelvoudigInformatieObject.objects.get(identificatie=zs_document_id)
                                    except EnkelvoudigInformatieObject.DoesNotExist as e:
                                        logger.error('[%s-%s] Object was %s but could not be found in the ZRC.', change_entry.id, object_id, change_type)
                                        failed += 1
                                    else:
                                        edc.update_cmis_properties(dms_document.properties, commit=not dryrun)
                                        updated += 1

                                else:
                                    zaak_folder = dms_document.getPaths()[0].split('/')[-2]
                                    created += 1
                        else:
                            if change_type == CMISChangeType.deleted:
                                if not dryrun:
                                    delete_count = (EnkelvoudigInformatieObject.objects.filter(_object_id=object_id)).delete()
                                    if delete_count[0] == 0:
                                        logger.warning('[%s-%s] Object was %s but could not be found in the ZRC.', change_entry.id, object_id, change_type)
                                        failed += 1
                                    else:
                                        deleted += 1
                                else:
                                    if change_type == CMISChangeType.security:
                                        logger.info('[%s-%s] Security changes are not processed.', change_entry.id, object_id)
                                        security += 1
                                    else:
                                        logger.error('[%s-%s] Unsupported change type: %s', change_entry.id, object_id, change_type)
                                        failed += 1
                    except Exception as e:
                        failed += 1
                        logger.exception(
                            '[%s-%s] Could not process "%s" in ZRC: %s',
                            change_entry.id,
                            object_id, change_type, e, exc_info=True
                        )

                if not dryrun and change_log:
                    change_log.status = ChangeLogStatus.completed
                    change_log.save()
                return OrderedDict([
                    (CMISChangeType.created, created),
                    (CMISChangeType.updated, updated),
                    (CMISChangeType.deleted, deleted),
                    (CMISChangeType.security, security),
                    ('failed', failed)
                ])


class DefaultClient(LazyObject):

    def _setup(self):
        client_cls = import_string(settings.CMIS_CLIENT_CLASS)
        self._wrapped = client_cls()


default_client = DefaultClient()
