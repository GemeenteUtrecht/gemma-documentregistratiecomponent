import datetime
import uuid

from django.utils import timezone

import factory
import factory.fuzzy
from faker import Faker
from vng_api_common.constants import ObjectTypes, VertrouwelijkheidsAanduiding


fake = Faker()
class EnkelvoudigInformatieObjectCanonicalFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'datamodel.EnkelvoudigInformatieObjectCanonical'


    latest_version = factory.RelatedFactory(
        'drc.datamodel.tests.factories.EnkelvoudigInformatieObjectFactory',
        'canonical'
    )


class EnkelvoudigInformatieObjectFactory(factory.django.DjangoModelFactory):
    canonical = factory.SubFactory(EnkelvoudigInformatieObjectCanonicalFactory)
    identificatie = factory.Sequence(lambda n: '{}{}'.format(uuid.uuid4().hex, n))
    bronorganisatie = factory.Faker('ssn', locale='nl_NL')
    creatiedatum = datetime.date(2018, 6, 27)
    titel = factory.Sequence(lambda n: 'some titel - {}'.format(n))
    auteur = 'some auteur'
    formaat = 'some formaat'
    taal = 'nld'
    inhoud = factory.django.FileField(data=fake.word().encode('utf-8'), filename=fake.file_name())
    informatieobjecttype = 'https://example.com/ztc/api/v1/catalogus/1/informatieobjecttype/1'
    vertrouwelijkheidaanduiding = VertrouwelijkheidsAanduiding.openbaar

    class Meta:
        model = 'datamodel.EnkelvoudigInformatieObject'


class ObjectInformatieObjectFactory(factory.django.DjangoModelFactory):

    informatieobject = factory.SubFactory(EnkelvoudigInformatieObjectCanonicalFactory)
    object = factory.Faker('url')

    class Meta:
        model = 'datamodel.ObjectInformatieObject'

    class Params:
        is_zaak = factory.Trait(
            object_type=ObjectTypes.zaak,
            object=factory.Sequence(lambda n: f'https://zrc.nl/api/v1/zaken/{n}'),
        )
        is_besluit = factory.Trait(
            object_type=ObjectTypes.besluit,
            object=factory.Sequence(lambda n: f'https://brc.nl/api/v1/besluiten/{n}')
        )


class GebruiksrechtenFactory(factory.django.DjangoModelFactory):
    informatieobject = factory.SubFactory(EnkelvoudigInformatieObjectCanonicalFactory)
    omschrijving_voorwaarden = factory.Faker('paragraph')

    class Meta:
        model = 'datamodel.Gebruiksrechten'

    @factory.lazy_attribute
    def startdatum(self):
        return datetime.datetime.combine(
            self.informatieobject.latest_version.creatiedatum,
            datetime.time(0, 0)
        ).replace(tzinfo=timezone.utc)
