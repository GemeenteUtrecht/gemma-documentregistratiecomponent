# uncompyle6 version 3.2.5
# Python bytecode 3.6 (3379)
# Decompiled from: Python 3.6.8 (default, Jan  2 2019, 05:35:58) 
# [GCC 8.2.0]
# Embedded file name: /home/jorik/sites/gemma-documentregistratiecomponent/src/drc/cmis/abstract.py
# Compiled at: 2018-11-15 15:26:24
# Size of source mod 2**32: 1792 bytes
from collections import OrderedDict
from io import BytesIO
from cmislib.atompub.binding import AtomPubDocument

class DRCClient:
    """
    Abstract base class for DRC interaction.
    """
    TEMP_FOLDER_NAME = '_temp'
    TRASH_FOLDER = 'Unfiled'

    def creeer_zaakfolder(self, zaak_url):
        raise NotImplementedError

    def maak_zaakdocument(self, document, zaak_url=None, filename=None, sender=None):
        raise NotImplementedError

    def maak_zaakdocument_met_inhoud(self, document, zaak_url=None, filename=None, sender=None, stream=None, content_type=None):
        raise NotImplementedError

    def geef_inhoud(self, document):
        raise NotImplementedError

    def zet_inhoud(self, document, stream, content_type=None, checkout_id=None):
        raise NotImplementedError

    def relateer_aan_zaak(self, document, zaak_url):
        raise NotImplementedError

    def update_zaakdocument(self, document, checkout_id=None, inhoud=None):
        raise NotImplementedError

    def checkout(self, document):
        raise NotImplementedError

    def cancel_checkout(self, document, checkout_id):
        raise NotImplementedError

    def ontkoppel_zaakdocument(self, document, zaak_url):
        raise NotImplementedError

    def is_locked(self, document):
        raise NotImplementedError

    def verwijder_document(self, document):
        raise NotImplementedError

    def sync(self, dryrun=False):
        raise NotImplementedError
# okay decompiling src/drc/cmis/__pycache__/abstract.cpython-36.pyc
# uncompyle6 version 3.2.5
# Python bytecode 3.6 (3379)
# Decompiled from: Python 3.6.8 (default, Jan  2 2019, 05:35:58) 
# [GCC 8.2.0]
# Embedded file name: /home/jorik/sites/gemma-documentregistratiecomponent/src/drc/cmis/apps.py
# Compiled at: 2018-11-19 15:48:16
# Size of source mod 2**32: 2565 bytes
from django.apps import AppConfig
from django.conf import settings
from django.core.checks import Error, Tags, register

class CMISConfig(AppConfig):
    name = 'drc.cmis'
    verbose_name = 'CMIS'

    def ready(self):
        if settings.CMIS_BACKEND_ENABLED:
            from . import signals
        register(check_cmis, Tags.compatibility, deploy=True)


def check_cmis(app_configs, **kwargs):
    """
    ZDS 1.2.01, hoofdstuk 5:
    Ten behoeve van de integratie met het ZS en het vastleggen van
    zaakdocumenten dient het DMS aan de volgende eisen te voldoen:
    
        * Het DMS wordt ontsloten als een CMIS 1.0 repository;
        * De CMIS-interface dient minimaal navolgende opties te ondersteunen:
            - "Multi-filing";
            - "Change Log", met registratie van Change Events voor
              filing/unfiling/moving van de objecten documenten en folders;
            - Nieuwe CMIS-objecttypes van het Base Type "cmis:document" en
              "cmis:folder" worden ondersteund;
        * De CMIS-changelog is toegankelijk voor het ZS.
    
    :param app_configs:
    :param kwargs:
    :return:
    """
    from .client import default_client as client
    from .choices import CMISCapabilities, CMISCapabilityChanges
    errors = []
    try:
        capabilities = client._repo.capabilities
    except Exception:
        errors.append(Error('Could not communicate with the DMS.',
          hint='Make sure the authentication and host settings are correct.'))
        return errors
    else:
        multifiling = capabilities.get(CMISCapabilities.multifiling, None)
        if not multifiling:
            errors.append(Error("The DMS does not support Multifiling, or it's disabled."))
        unfiling = capabilities.get(CMISCapabilities.unfiling, None)
        if not unfiling:
            errors.append(Error("The DMS does not support Unfiling or it's disabled."))
        changes = capabilities.get(CMISCapabilities.changes, None)
        if not changes or changes == CMISCapabilityChanges.none:
            errors.append(Error("The DMS does not support Change Log, or it's disabled.",
              hint="In case you're running Alfresco, make sure to add the relevant audit.* properties."))

    return errors
# okay decompiling src/drc/cmis/__pycache__/apps.cpython-36.pyc
# uncompyle6 version 3.2.5
# Python bytecode 3.6 (3379)
# Decompiled from: Python 3.6.8 (default, Jan  2 2019, 05:35:58) 
# [GCC 8.2.0]
# Embedded file name: /home/jorik/sites/gemma-documentregistratiecomponent/src/drc/cmis/choices.py
# Compiled at: 2018-11-12 14:45:44
# Size of source mod 2**32: 5453 bytes
from django.utils.translation import ugettext as _
from djchoices import ChoiceItem, DjangoChoices

class CMISChangeType(DjangoChoices):
    created = ChoiceItem('created', _('Created'))
    updated = ChoiceItem('updated', _('Updated'))
    deleted = ChoiceItem('deleted', _('Deleted'))
    security = ChoiceItem('security', _('Security'))


class CMISObjectType(DjangoChoices):
    zaken = ChoiceItem('F:zsdms:zaken', _('Zaken hoofd folder'))
    zaak_folder = ChoiceItem('F:zsdms:zaak', _('Zaak folder'))
    edc = ChoiceItem('D:zsdms:document', _('Enkelvoudig document'))


class CMISCapabilities(DjangoChoices):
    """
    http://docs.oasis-open.org/cmis/CMIS/v1.0/cmis-spec-v1.0.html
    """
    changes = ChoiceItem('Changes', _('Indicates what level of changes (if any) the repository exposes via the "change log" service.'))
    all_versions_searchable = ChoiceItem('AllVersionsSearchable', _('Ability of the Repository to include all versions of document. If False, typically either the latest or the latest major version will be searchable.'))
    content_stream_updatability = ChoiceItem('ContentStreamUpdatability', _("Indicates the support a repository has for updating a document's content stream."))
    pwc_updatable = ChoiceItem('PWCUpdatable', _('Ability for an application to update the "Private Working Copy" of a checked-out document.'))
    pwc_searchable = ChoiceItem('PWCSearchable', _('Ability of the Repository to include the "Private Working Copy" of checked-out documents in query search scope; otherwise PWC\'s are not searchable'))
    unfiling = ChoiceItem('Unfiling', _('Ability for an application to leave a document or other file-able object not filed in any folder.'))
    multifiling = ChoiceItem('Multifiling', _('Ability for an application to file a document or other file-able object in more than one folder.'))
    version_specific_filing = ChoiceItem('VersionSpecificFiling', _('Ability for an application to file individual versions (i.e., not all versions) of a document in a folder.'))
    renditions = ChoiceItem('Renditions', _('Indicates whether or not the repository exposes renditions of document or folder objects.'))
    query = ChoiceItem('Query', _('Indicates the types of queries that the Repository has the ability to fulfill.'))
    get_folder_tree = ChoiceItem('GetFolderTree', _('Ability for an application to retrieve the folder tree via the getFolderTree service.'))
    acl = ChoiceItem('ACL', _('Indicates the level of support for ACLs by the repository.'))
    join = ChoiceItem('Join', _(' Indicates the types of JOIN keywords that the Repository can fulfill in queries.'))


class CMISCapabilityContentStreamUpdatability(DjangoChoices):
    none = ChoiceItem('none', _(' The content stream may never be updated.'))
    anytime = ChoiceItem('anytime', _(' The content stream may be updated any time.'))
    pwconly = ChoiceItem('pwconly', _(' The content stream may be updated only when checked out.'))


class CMISCapabilityRenditions(DjangoChoices):
    read = ChoiceItem('read', _(' Renditions are provided by the repository and readable by the client.'))
    none = ChoiceItem('none', _(' The repository does not expose renditions at all.'))


class CMISCapabilityQuery(DjangoChoices):
    none = ChoiceItem('none', _(' No queries of any kind can be fulfilled.'))
    metadataonly = ChoiceItem('metadataonly', _(' Only queries that filter based on object properties can be fulfilled. Specifically, the CONTAINS() predicate function is not supported.'))
    fulltextonly = ChoiceItem('fulltextonly', _(' Only queries that filter based on the full-text content of documents can be fulfilled. Specifically, only the CONTAINS() predicate function can be included in the WHERE clause.'))
    bothseparate = ChoiceItem('bothseparate', _(' The repository can fulfill queries that filter EITHER on the full-text content of documents OR on their properties, but NOT if both types of filters are included in the same query.'))
    bothcombined = ChoiceItem('bothcombined', _(' The repository can fulfill queries that filter on both the full-text content of documents and their properties in the same query.'))


class CMISCapabilityChanges(DjangoChoices):
    none = ChoiceItem('none', _(' The repository does not support the change log feature.'))
    objectidsonly = ChoiceItem('objectidsonly', _(' The change log can return only the ObjectIDs for changed objects in the repository and an indication of the type of change, not details of the actual change.'))
    properties = ChoiceItem('properties', _(' The change log can return properties and the ObjectID for the changed objects'))
    all = ChoiceItem('all', _(' The change log can return the ObjectIDs for changed objects in the repository and more information about the actual change'))


class CMISCapabilityACL(DjangoChoices):
    none = ChoiceItem('none', _(' The repository does not support ACL services'))
    discover = ChoiceItem('discover', _(' The repository supports discovery of ACLs (getACL and other services)'))
    manage = ChoiceItem('manage', _(' The repository supports discovery of ACLs AND applying ACLs (getACL and applyACL services)'))


class ChangeLogStatus(DjangoChoices):
    completed = ChoiceItem('completed', _('Completed'))
    in_progress = ChoiceItem('in_progress', _('In progress'))
# okay decompiling src/drc/cmis/__pycache__/choices.cpython-36.pyc
# uncompyle6 version 3.2.5
# Python bytecode 3.6 (3379)
# Decompiled from: Python 3.6.8 (default, Jan  2 2019, 05:35:58) 
# [GCC 8.2.0]
# Embedded file name: /home/jorik/sites/gemma-documentregistratiecomponent/src/drc/cmis/client.py
# Compiled at: 2018-11-19 11:50:17
# Size of source mod 2**32: 25847 bytes
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
from cmislib.atompub.binding import AtomPubDocument, AtomPubFolder
from cmislib.exceptions import ObjectNotFoundException, UpdateConflictException
from .abstract import DRCClient
from .choices import ChangeLogStatus, CMISChangeType, CMISObjectType
from .exceptions import DocumentConflictException, DocumentDoesNotExistError, DocumentExistsError, DocumentLockedException, SyncException
from .models import ChangeLog
from .query import CMISQuery
from .utils import FolderConfig, get_cmis_object_id
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
            return (
             existing, False)
            return (
             parent.createFolder(name, properties=properties or {}), True)

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
        if not len(result_set):
            raise DocumentDoesNotExistError(('Document met identificatie {} bestaat niet in het DRC').format(document.identificatie))
        doc = [item for item in result_set][0]
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
        if not settings.CMIS_ZAKEN_TYPE_ENABLED:
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
        In afwijking van de KING specificatie waarbij het document aanmaken
        en het document van inhoud voorzien aparte stappen zijn, wordt in deze
        functie in 1 stap het document aangemaakt met inhoud. Dit voorkomt dat
        er in het DRC direct een versie 1.1 ontstaat, waarbij versie 1.0 een
        leeg document betreft, en versie 1.1 het eigenlijke document pas is.
        
        :param zaak: TODO
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
        _doc = self._repo.createDocument(name=document.titel,
          properties=properties,
          contentFile=stream,
          contentType=content_type,
          parentFolder=zaakfolder)
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
            return (
             None, BytesIO())

        filename = doc.properties['cmis:name']
        empty = doc.properties['cmis:contentStreamId'] is None
        if empty:
            return (filename, BytesIO())
            return (
             filename, doc.getContentStream())

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
        cmis_doc = checkout_idcmis_doccmis_doc.getPrivateWorkingCopy()
        cmis_doc.setContentStream(stream, content_type)

    def update_zaakdocument(self, document, checkout_id=None, inhoud=None):
        cmis_doc = self._get_cmis_doc(document, checkout_id=checkout_id)
        cmis_doc = checkout_idcmis_doccmis_doc.getPrivateWorkingCopy()
        current_properties = cmis_doc.properties
        new_properties = self._build_cmis_doc_properties(document,
          filename=inhoud.bestandsnaam if inhoud else None)
        diff_properties = {key:value for key, value in new_properties.items() if current_properties.get(key) != new_properties.get(key)}
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
        return (
         checkout_id, checkout_by)

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
                change_log = None
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
                        logger.exception('[%s-%s] Could not process "%s" in ZRC: %s',
                          change_entry.id,
                          object_id, change_type, e, exc_info=True)

                if not dryrun:
                    change_log.status = ChangeLogStatus.completed
                    change_log.save()
                return OrderedDict([
                 (
                  CMISChangeType.created, created),
                 (
                  CMISChangeType.updated, updated),
                 (
                  CMISChangeType.deleted, deleted),
                 (
                  CMISChangeType.security, security),
                 (
                  'failed', failed)])


class DefaultClient(LazyObject):

    def _setup(self):
        client_cls = import_string(settings.CMIS_CLIENT_CLASS)
        self._wrapped = client_cls()


default_client = DefaultClient()
# okay decompiling src/drc/cmis/__pycache__/client.cpython-36.pyc
# uncompyle6 version 3.2.5
# Python bytecode 3.6 (3379)
# Decompiled from: Python 3.6.8 (default, Jan  2 2019, 05:35:58) 
# [GCC 8.2.0]
# Embedded file name: /home/jorik/sites/gemma-documentregistratiecomponent/src/drc/cmis/exceptions.py
# Compiled at: 2018-11-09 16:36:11
# Size of source mod 2**32: 310 bytes


class DMSException(Exception):
    pass


class DocumentExistsError(DMSException):
    pass


class DocumentDoesNotExistError(DMSException):
    pass


class SyncException(DMSException):
    pass


class DocumentConflictException(DMSException):
    pass


class DocumentLockedException(DMSException):
    pass
# okay decompiling src/drc/cmis/__pycache__/exceptions.cpython-36.pyc
# uncompyle6 version 3.2.5
# Python bytecode 3.6 (3379)
# Decompiled from: Python 3.6.8 (default, Jan  2 2019, 05:35:58) 
# [GCC 8.2.0]
# Embedded file name: /home/jorik/sites/gemma-documentregistratiecomponent/src/drc/cmis/__init__.py
# Compiled at: 2018-11-09 16:34:44
# Size of source mod 2**32: 48 bytes
default_app_config = 'drc.cmis.apps.CMISConfig'
# okay decompiling src/drc/cmis/__pycache__/__init__.cpython-36.pyc
# uncompyle6 version 3.2.5
# Python bytecode 3.6 (3379)
# Decompiled from: Python 3.6.8 (default, Jan  2 2019, 05:35:58) 
# [GCC 8.2.0]
# Embedded file name: /home/jorik/sites/gemma-documentregistratiecomponent/src/drc/cmis/models.py
# Compiled at: 2018-11-16 11:49:18
# Size of source mod 2**32: 1847 bytes
from django.core.exceptions import FieldDoesNotExist
from django.db import models
from .choices import ChangeLogStatus
from .utils import get_model_field, get_model_value

class ChangeLog(models.Model):
    token = models.BigIntegerField()
    created_on = models.DateTimeField(auto_now_add=True, unique=True)
    status = models.CharField(max_length=20, choices=ChangeLogStatus.choices, default=ChangeLogStatus.in_progress)

    class Meta:
        verbose_name = 'Changelog'
        verbose_name_plural = 'Changelogs'
        ordering = ('created_on', )


class CMISMixin(models.Model):
    CMIS_MAPPING = None

    class Meta:
        abstract = True

    def get_cmis_properties(self, allow_none=True):
        """
        Returns the CMIS properties as dict.
        
        :param allow_none: Converts `None` to  empty string if `False` (default).
        :return: The `dict` of CMIS properties.
        """
        result = {}
        for cmis_property, field_name in self.CMIS_MAPPING.items():
            try:
                field_class = get_model_field(self.__class__, field_name)
            except FieldDoesNotExist:
                field_class = None

            val = get_model_value(self, field_name)
            if val is None:
                if not allow_none:
                    val = ''
            result[cmis_property] = val

        return result

    cmis_properties = property(get_cmis_properties)

    def update_cmis_properties(self, new_cmis_properties, commit=False):
        """
        Only mapped properties are handled. Other properties passed to
        `new_cmis_properties` are ignored.
        
        :param new_cmis_properties: A `dict` of CMIS properties.
        :param commit: Indicate whether the updated objects should be saved.
        :return: A `set` of updated model instances.
        """
        raise NotImplementedError()
# okay decompiling src/drc/cmis/__pycache__/models.cpython-36.pyc
# uncompyle6 version 3.2.5
# Python bytecode 3.6 (3379)
# Decompiled from: Python 3.6.8 (default, Jan  2 2019, 05:35:58) 
# [GCC 8.2.0]
# Embedded file name: /home/jorik/sites/gemma-documentregistratiecomponent/src/drc/cmis/query.py
# Compiled at: 2018-11-15 16:14:27
# Size of source mod 2**32: 954 bytes


class CMISQuery:
    """
    Small, not feature-complete utility class for building CMIS queries with
    escaping built in.
    
    Usage:
    >>> query = CMSQuery("SELECT * FROM cmis:document WHERE cmis:objectTypeId = '%s'")
    >>> query('zsdms:document')
    "SELECT * FROM cmis:document WHERE cmis:objectTypeId = 'zsdms:document';"
    """

    def __init__(self, query):
        self.query = query

    def __call__(self, *args):
        args = tuple((self.escape(arg) for arg in args))
        return self.query % args

    def escape(self, value):
        """
        Escapes the characters in value for the CMIS queries.
        
        Poor documentation references:
          * https://community.alfresco.com/docs/DOC-5898-cmis-query-language#Literals
          * http://docs.alfresco.com/community/concepts/rm-searchsyntax-literals.html
        """
        value = value.replace("'", "\\'")
        value = value.replace('"', '\\"')
        return value
# okay decompiling src/drc/cmis/__pycache__/query.cpython-36.pyc
# uncompyle6 version 3.2.5
# Python bytecode 3.6 (3379)
# Decompiled from: Python 3.6.8 (default, Jan  2 2019, 05:35:58) 
# [GCC 8.2.0]
# Embedded file name: /home/jorik/sites/gemma-documentregistratiecomponent/src/drc/cmis/signals.py
# Compiled at: 2018-11-19 16:36:22
# Size of source mod 2**32: 1707 bytes
"""
Signal handlers voor DRC-CMIS interactie.
"""
from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from drc.datamodel.models import EnkelvoudigInformatieObject, ObjectInformatieObject
from .client import default_client as client

@receiver(post_save, sender=ObjectInformatieObject, dispatch_uid='cmis.creeer_zaakfolder')
def creeer_zaakfolder(signal, instance, **kwargs):
    if not kwargs['created'] or kwargs['raw']:
        return
        transaction.on_commit(lambda : (
         client.creeer_zaakfolder(instance.object),
         client.relateer_aan_zaak(instance.informatieobject, instance.object)),
          using=kwargs['using'])


@receiver(post_save, sender=EnkelvoudigInformatieObject, dispatch_uid='cmis.creeer_document')
def creeer_document(signal, instance, **kwargs):
    if not kwargs['created'] or kwargs['raw']:
        return
        transaction.on_commit(lambda : (client.maak_zaakdocument_met_inhoud(instance, stream=instance.inhoud.file)),
          using=kwargs['using'])


@receiver(post_delete, sender=ObjectInformatieObject, dispatch_uid='cmis.ontkoppel_zaakdocument')
def ontkoppel_zaakdocument(signal, instance, **kwargs):
    client.relateer_aan_zaak(instance.informatieobject, instance.object)


@receiver(post_delete, sender=EnkelvoudigInformatieObject, dispatch_uid='cmis.verwijder_document')
def verwijder_document(signal, instance, **kwargs):
    client.verwijder_document(instance)
# okay decompiling src/drc/cmis/__pycache__/signals.cpython-36.pyc
# uncompyle6 version 3.2.5
# Python bytecode 3.6 (3379)
# Decompiled from: Python 3.6.8 (default, Jan  2 2019, 05:35:58) 
# [GCC 8.2.0]
# Embedded file name: /home/jorik/sites/gemma-documentregistratiecomponent/src/drc/cmis/storage.py
# Compiled at: 2018-11-19 12:57:22
pass
# okay decompiling src/drc/cmis/__pycache__/storage.cpython-36.pyc
# uncompyle6 version 3.2.5
# Python bytecode 3.6 (3379)
# Decompiled from: Python 3.6.8 (default, Jan  2 2019, 05:35:58) 
# [GCC 8.2.0]
# Embedded file name: /home/jorik/sites/gemma-documentregistratiecomponent/src/drc/cmis/utils.py
# Compiled at: 2018-11-16 11:50:28
# Size of source mod 2**32: 3761 bytes
from django.contrib.admin.utils import get_fields_from_path
from django.db.models.constants import LOOKUP_SEP
from .choices import CMISObjectType

def get_cmis_object_id_parts(cmis_object_id):
    """
    Returns the actual object ID, version and path, if present.
    
    :param object_id: A `CmisId`.
    :return: A `tuple` containing the actual object Id, version and path as strings.
    """
    parts = cmis_object_id.split(';')
    version = None
    if len(parts) == 2:
        version = parts[1]
    parts = parts[0].rsplit('/')
    object_id = parts[-1]
    path = None
    if len(parts) == 2:
        path = parts[0]
    return (
     object_id, version, path)


def get_cmis_object_id(cmis_object_id):
    """
    Returns the actual object ID.
    
    :param object_id: A `CmisId`.
    :return: The actual CMIS Id as string.
    """
    return get_cmis_object_id_parts(cmis_object_id)[0]


class FolderConfig:
    __slots__ = [
     'type', 'name']

    def __init__(self, type_=None, name=None):
        if not type_:
            if not name:
                raise AssertionError('Either type or name is required')
        self.type = type_
        self.name = name

    def __repr__(self):
        return ('<{} type_={!r} name={!r}>').format(self.__class__.__name__, self.type, self.name)


def upload_to(zaak):
    """
    Return the fully qualified upload path for the zaak, generic case.
    
    Each item from the return list is a FolderConfig object with either a
    type, name or both defined. If a name is defined, this name will be used
    for the folder name. The type is required to be able to generate the
    appropriate cmis properties.
    
    :param zaak: :class:`zaakmagazijn.rgbz.models.Zaak` instance.
    :return: list of FolderConfig objects, in order of root -> leaf
    """
    return [
     FolderConfig(name='Zaken', type_=CMISObjectType.zaken),
     FolderConfig(type_=CMISObjectType.zaak_folder)]


def upload_to_date_based(zaak):
    """
    Return the fully qualified upload path for the zaak, Haarlem variant.
    
    Each item from the return list is a FolderConfig object with either a
    type, name or both defined. If a name is defined, this name will be used
    for the folder name. The type is required to be able to generate the
    appropriate cmis properties.
    
    :param zaak: :class:`zaakmagazijn.rgbz.models.Zaak` instance.
    :return: list of FolderConfig objects, in order of root -> leaf
    """
    if not len(zaak.startdatum) == 8:
        raise AssertionError('Zaak.startdatum moet volledig bekend zijn')
    year, month, day = zaak.startdatum[0:4], zaak.startdatum[4:6], zaak.startdatum[6:8]
    return [
     FolderConfig(name='Sites'),
     FolderConfig(name='archief'),
     FolderConfig(name='documentLibrary', type_=CMISObjectType.zaken),
     FolderConfig(type_=CMISObjectType.zaaktype),
     FolderConfig(name=year),
     FolderConfig(name=month),
     FolderConfig(name=day),
     FolderConfig(type_=CMISObjectType.zaak_folder)]


def get_model_value(obj, field_name):
    """
    Returns the value belonging to `field_name` on `Model` instance.
    This works for related fields.
    
    Example::
    
        >>> get_model_value(Zaak, 'zaaktype__zaaktypeomschrijving')
        'Some description'
    
    """
    fields = field_name.split(LOOKUP_SEP)
    for field in fields:
        obj = getattr(obj, field)

    return obj


def get_model_field(model, field_name):
    """
    Returns the `Field` instance belonging to `field_name` on a `Model`
    instance or class. This works for related fields.
    
    Example::
    
        >>> get_model_field(Zaak, 'zaaktype__zaaktypeomschrijving')
        <django.db.models.fields.CharField: zaaktypeomschrijving>
    
    """
    return get_fields_from_path(model, field_name)[-1]
# okay decompiling src/drc/cmis/__pycache__/utils.cpython-36.pyc
# decompiled 11 files: 11 okay, 0 failed
