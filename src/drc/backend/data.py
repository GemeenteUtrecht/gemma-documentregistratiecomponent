from dataclasses import dataclass
from datetime import date, datetime
from typing import Dict, Optional


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
    status: str
    beschrijving: str
    indicatie_gebruiksrecht: Optional[bool]
    ondertekening_soort: str
    informatieobjecttype: str
    formaat: str
    taal: str
    bestandsnaam: str
    link: str
    integriteit_algoritme: str
    integriteit_waarde: str
    bestandsomvang: str
    begin_registratie: datetime
    versie: str
    locked: bool

    def __post_init__(self):
        # FIXME - this is NOT a default, but required for the archiving flow
        # with Contezza
        self.indicatie_gebruiksrecht = self.indicatie_gebruiksrecht or False

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

    @property
    def integriteit(self) -> Dict[str, str]:
        return {
            "algoritme": self.integriteit_algoritme,
            "waarde": self.integriteit_waarde,
            "datum": self.integriteit_datum,
        }

    @property
    def ondertekening(self) -> Dict[str, str]:
        return {
            "soort": self.ondertekening_soort,
            "datum": self.ondertekening_datum,
        }


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
