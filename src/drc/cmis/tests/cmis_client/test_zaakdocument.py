from datetime import date, datetime
from io import BytesIO
from unittest import skipIf

from django.conf import settings
from django.db.models import signals
from django.test import TestCase, override_settings

import factory
import pytz

from drc.datamodel.tests.factories import EnkelvoudigInformatieObjectFactory

from ...exceptions import DocumentExistsError
from ..mixins import DMSMixin


@skipIf(not settings.CMIS_BACKEND_ENABLED, "Skipped if CMIS should not be active")
@factory.django.mute_signals(signals.post_save)
class CMISClientTests(DMSMixin, TestCase):
    def test_maak_zaakdocument(self):
        self.cmis_client.creeer_zaakfolder(self.zaak_url)
        document = EnkelvoudigInformatieObjectFactory.create(
            titel='testnaam',
            ontvangstdatum=date(2017, 1, 1),
            beschrijving='Een beschrijving',
        )

        # cmis_doc = self.cmis_client._get_cmis_doc(document)
        cmis_doc = self.cmis_client.maak_zaakdocument(document, self.zaak_url)

        # verify that it identifications are unique
        with self.assertRaises(DocumentExistsError):
            self.cmis_client.maak_zaakdocument(document, self.zaak_url)

        document.refresh_from_db()
        # verify expected props
        self.assertExpectedProps(cmis_doc, {
            'cmis:contentStreamFileName': 'testnaam',
            'cmis:contentStreamLength': 0,
            'cmis:contentStreamMimeType': 'application/binary',
            'zsdms:dct.omschrijving': document.informatieobjecttype,
            'zsdms:documentIdentificatie': document.identificatie,
            'zsdms:documentauteur': document.auteur,
            'zsdms:documentbeschrijving': 'Een beschrijving',
            'zsdms:documentcreatiedatum': datetime.combine(document.creatiedatum, datetime.min.time()).replace(tzinfo=pytz.utc),
            'zsdms:documentLink': None,
            'zsdms:documentontvangstdatum': datetime.combine(document.ontvangstdatum, datetime.min.time()).replace(tzinfo=pytz.utc),
            'zsdms:documentstatus': None,
            'zsdms:documenttaal': document.taal,
            'zsdms:documentversie': None,
            'zsdms:documentverzenddatum': None,
            'zsdms:vertrouwelijkaanduiding': document.vertrouwelijkheidaanduiding
        })

        self.assertEqual(
            document._object_id,
            cmis_doc.properties['cmis:objectId'].rsplit(';')[0]
        )

    def test_maak_zaakdocument_met_gevulde_inhoud(self):
        self.cmis_client.creeer_zaakfolder(self.zaak_url)

        document = EnkelvoudigInformatieObjectFactory.create(
            titel='testnaam',
            ontvangstdatum=date(2017, 1, 1),
            beschrijving='Een beschrijving',
        )

        cmis_doc = self.cmis_client.maak_zaakdocument_met_inhoud(document, self.zaak_url, stream=BytesIO(b'test'))
        self.assertExpectedProps(cmis_doc, {
            'cmis:contentStreamFileName': 'testnaam',
            'cmis:contentStreamLength': 4,
            'cmis:contentStreamMimeType': 'application/binary',
            'zsdms:dct.omschrijving': document.informatieobjecttype,
            'zsdms:documentIdentificatie': document.identificatie,
            'zsdms:documentauteur': document.auteur,
            'zsdms:documentbeschrijving': 'Een beschrijving',
            'zsdms:documentcreatiedatum': datetime.combine(document.creatiedatum, datetime.min.time()).replace(tzinfo=pytz.utc),
            'zsdms:documentLink': None,
            'zsdms:documentontvangstdatum': datetime.combine(document.ontvangstdatum, datetime.min.time()).replace(tzinfo=pytz.utc),
            'zsdms:documentstatus': None,
            'zsdms:documenttaal': document.taal,
            'zsdms:documentversie': None,
            'zsdms:documentverzenddatum': None,
            'zsdms:vertrouwelijkaanduiding': document.vertrouwelijkheidaanduiding
        })

        document.refresh_from_db()
        self.assertEqual(
            document._object_id,
            cmis_doc.properties['cmis:objectId'].rsplit(';')[0]
        )

    @override_settings(CMIS_SENDER_PROPERTY='zsdms:documentauteur')
    def test_maak_zaakdocument_met_sender_property(self):
        self.cmis_client.creeer_zaakfolder(self.zaak_url)

        document = EnkelvoudigInformatieObjectFactory.create(
            titel='testnaam',
            ontvangstdatum=date(2017, 1, 1),
            beschrijving='Een beschrijving',
        )

        cmis_doc = self.cmis_client.maak_zaakdocument_met_inhoud(document, self.zaak_url, sender='maykin', stream=BytesIO(b'test'))
        self.assertExpectedProps(cmis_doc, {
            'cmis:contentStreamFileName': 'testnaam',
            'cmis:contentStreamLength': 4,
            'cmis:contentStreamMimeType': 'application/binary',
            'zsdms:dct.omschrijving': document.informatieobjecttype,
            'zsdms:documentIdentificatie': document.identificatie,
            'zsdms:documentauteur': 'maykin',  # overridden by the sender
            'zsdms:documentbeschrijving': 'Een beschrijving',
            'zsdms:documentcreatiedatum': datetime.combine(document.creatiedatum, datetime.min.time()).replace(tzinfo=pytz.utc),
            'zsdms:documentLink': None,
            'zsdms:documentontvangstdatum': datetime.combine(document.ontvangstdatum, datetime.min.time()).replace(tzinfo=pytz.utc),
            'zsdms:documentstatus': None,
            'zsdms:documenttaal': document.taal,
            'zsdms:documentversie': None,
            'zsdms:documentverzenddatum': None,
            'zsdms:vertrouwelijkaanduiding': document.vertrouwelijkheidaanduiding
        })

        document.refresh_from_db()
        self.assertEqual(
            document._object_id,
            cmis_doc.properties['cmis:objectId'].rsplit(';')[0]
        )

    def test_lees_document(self):
        """
        Ref #83: geefZaakdocumentLezen vraagt een kopie van het bestand op.

        Van het bestand uit het DMS wordt opgevraagd: inhoud, bestandsnaam.
        """
        self.cmis_client.creeer_zaakfolder(self.zaak_url)
        document = EnkelvoudigInformatieObjectFactory.create(identificatie='123456')
        cmis_doc = self.cmis_client.maak_zaakdocument(document, self.zaak_url)

        # empty by default
        filename, file_obj = self.cmis_client.geef_inhoud(document)

        self.assertEqual(filename, document.titel)
        self.assertEqual(file_obj.read(), b'')

        cmis_doc.setContentStream(BytesIO(b'some content'), 'text/plain')

        filename, file_obj = self.cmis_client.geef_inhoud(document)

        self.assertEqual(filename, document.titel)
        self.assertEqual(file_obj.read(), b'some content')

    def test_lees_document_bestaad_niet(self):
        """
        Ref #83: geefZaakdocumentLezen vraagt een kopie van het bestand op.

        Van het bestand uit het DMS wordt opgevraagd: inhoud, bestandsnaam.
        """
        self.cmis_client.creeer_zaakfolder(self.zaak_url)
        document = EnkelvoudigInformatieObjectFactory.build(identificatie='123456')

        # empty by default
        filename, file_obj = self.cmis_client.geef_inhoud(document)

        self.assertEqual(filename, None)
        self.assertEqual(file_obj.read(), b'')

    def test_voeg_zaakdocument_toe(self):
        """
        4.3.4.3 Interactie tussen ZS en DMS

        Het ZS zorgt ervoor dat het document dat is aangeboden door de DSC wordt vastgelegd in het DMS.
        Hiervoor maakt het ZS gebruik van de CMIS-services die aangeboden worden door het DMS. Hierbij
        gelden de volgende eisen:
        - Het document wordt gerelateerd aan de juiste Zaakfolder (Zie 5.1)
        - Het document wordt opgeslagen als objecttype EDC (Zie 5.2)
        - Minimaal de vereiste metadata voor een EDC wordt vastgelegd in de daarvoor gedefinieerde
        objectproperties. In Tabel 3 is een mapping aangegeven tussen de StUF-ZKN-elementen en
        CMIS-objectproperties.
        """
        document = EnkelvoudigInformatieObjectFactory.create(
            titel='testnaam', beschrijving='Een beschrijving'
        )
        self.cmis_client.maak_zaakdocument(document)
        document.refresh_from_db()

        result = self.cmis_client.zet_inhoud(document, BytesIO(b'some content'), content_type='text/plain')

        self.assertIsNone(result)
        filename, file_obj = self.cmis_client.geef_inhoud(document)
        self.assertEqual(file_obj.read(), b'some content')
        self.assertEqual(filename, document.titel)

    def test_relateer_aan_zaak(self):
        document = EnkelvoudigInformatieObjectFactory.create(
            titel='testnaam', beschrijving='Een beschrijving'
        )
        zaak_folder = self.cmis_client.creeer_zaakfolder(self.zaak_url)
        self.cmis_client.maak_zaakdocument(document)
        document.refresh_from_db()

        result = self.cmis_client.relateer_aan_zaak(document, self.zaak_url)
        self.assertIsNone(result)

        cmis_doc = self.cmis_client._get_cmis_doc(document)
        parents = [parent.id for parent in cmis_doc.getObjectParents()]
        self.assertEqual(parents, [zaak_folder.id])

    def test_ontkoppel_zaakdocument(self):
        cmis_folder = self.cmis_client.creeer_zaakfolder(self.zaak_url)
        document = EnkelvoudigInformatieObjectFactory.create(
            titel='testnaam', beschrijving='Een beschrijving'
        )
        self.cmis_client.maak_zaakdocument(document, self.zaak_url)
        result = self.cmis_client.ontkoppel_zaakdocument(document, self.zaak_url)
        self.assertIsNone(result)

        # check that the zaakfolder is empty
        self.assertFalse(cmis_folder.getChildren())

    def test_verwijder_document(self):
        zaak_folder = self.cmis_client.creeer_zaakfolder(self.zaak_url)
        document = EnkelvoudigInformatieObjectFactory.create(
            titel='testnaam', beschrijving='Een beschrijving'
        )
        self.cmis_client.maak_zaakdocument(document, self.zaak_url)

        result = self.cmis_client.verwijder_document(document)

        self.assertIsNone(result)
        # check that it's gone
        trash_folder, _ = self.cmis_client._get_or_create_folder(self.cmis_client.TRASH_FOLDER)
        self.assertEqual(len(trash_folder.getChildren()), 0)
        self.assertEqual(len(zaak_folder.getChildren()), 0)
