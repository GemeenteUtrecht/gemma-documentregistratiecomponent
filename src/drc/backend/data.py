from dataclasses import dataclass, field
from datetime import date, datetime


@dataclass
class PaginationObject:
    count: int
    results: list
    next: str = None
    previous: str = None


@dataclass
class EnkelvoudigInformatieObject:
    url: str
    inhoud: str
    creatiedatum: date
    ontvangstdatum: date
    verzenddatum: date
    integriteit_datum: date
    ondertekening_datum: date
    titel: str
    identificatie: str
    bronorganisatie: str
    vertrouwelijkheidaanduiding: str
    auteur: str
    status: str = field(default="")
    beschrijving: str = field(default="")
    indicatie_gebruiksrecht: str
    ondertekening_soort: str
    informatieobjecttype: str
    formaat: str = field(default="")
    taal: str
    bestandsnaam: str = field(default="")
    link: str = field(default="")
    integriteit_algoritme: str
    integriteit_waarde: str
    bestandsomvang: str
    begin_registratie: datetime
    versie: str
    locked: bool

    #TODO: Fix a little better
    @property
    def latest_version(self):
        return self

    def unique_representation(self):
        return f"{self.bronorganisatie} - {self.identificatie}"

    @property
    def uuid(self):
        return self.url.split('/')[-1]

    @property
    def beginRegistratie(self):
        return self.begin_registratie.isoformat().replace('+00:00', 'Z')

    def update(self):
        from .adapter import drc_storage_adapter
        lock = drc_storage_adapter.lock_enkelvoudiginformatieobject(self.uuid)
        data = self.__dict__.copy()
        del data['inhoud']
        del data['url']
        del data['bestandsomvang']
        data = {k: v for k, v in data.items() if v is not None}
        drc_storage_adapter.update_enkenvoudiginformatieobject(self.uuid, lock, data)
        return drc_storage_adapter.unlock_enkelvoudiginformatieobject(self.uuid, lock)


@dataclass
class ObjectInformatieObject:
    url: str
    informatieobject: str
    object: str
    object_type: str
    aard_relatie: str
    titel: str
    beschrijving: str
    registratiedatum: str

    @property
    def get_informatieobject(self):
        from .adapter import drc_storage_adapter
        return drc_storage_adapter.lees_enkelvoudiginformatieobject(uuid=self.informatieobject.split('/')[-1])

    @property
    def uuid(self):
        return self.url.split('/')[-1]
