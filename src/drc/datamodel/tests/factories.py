import datetime
import uuid

from django.utils import timezone

import factory
import factory.fuzzy
from faker import Faker
from vng_api_common.constants import ObjectTypes, VertrouwelijkheidsAanduiding

from drc.backend import drc_storage_adapter

fake = Faker()


# class EnkelvoudigInformatieObjectCanonicalFactory(factory.django.DjangoModelFactory):
#     class Meta:
#         model = 'datamodel.EnkelvoudigInformatieObjectCanonical'

#     latest_version = factory.RelatedFactory(
#         'drc.datamodel.tests.factories.EnkelvoudigInformatieObjectFactory',
#         'canonical'
#     )


class EnkelvoudigInformatieObjectFactory(factory.django.DjangoModelFactory):
    # canonical = factory.SubFactory(EnkelvoudigInformatieObjectCanonicalFactory)
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

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Create an instance of the model, and save it to the database."""
        from drc.backend import drc_storage_adapter
        from factory import builder
        step = builder.StepBuilder(cls._meta, kwargs, 'build')
        values = step.build()
        eio = drc_storage_adapter.creeer_enkelvoudiginformatieobject(values.__dict__)
        return eio


class ObjectInformatieObjectFactory(factory.django.DjangoModelFactory):
    # informatieobject = factory.SubFactory(EnkelvoudigInformatieObjectCanonicalFactory)
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

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Create an instance of the model, and save it to the database."""
        from drc.backend import drc_storage_adapter
        from factory import builder
        step = builder.StepBuilder(cls._meta, kwargs, 'build')
        values = step.build()
        assert False, values.__dict__
        oio = drc_storage_adapter.creeer_objectinformatieobject(values.__dict__)
        return oio


class GebruiksrechtenFactory(factory.django.DjangoModelFactory):
    # informatieobject = factory.SubFactory(EnkelvoudigInformatieObjectCanonicalFactory)
    omschrijving_voorwaarden = factory.Faker('paragraph')

    class Meta:
        model = 'datamodel.Gebruiksrechten'

    @factory.lazy_attribute
    def startdatum(self):
        eio = drc_storage_adapter.lees_enkelvoudiginformatieobject(self.informatieobject.split('/')[-1])
        return datetime.datetime.combine(
            eio.creatiedatum,
            datetime.time(0, 0)
        ).replace(tzinfo=timezone.utc)
