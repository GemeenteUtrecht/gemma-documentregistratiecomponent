from dataclasses import dataclass
from datetime import date


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
    indicatie_gebruiksrecht: str
    ondertekening_soort: str
    informatieobjecttype: str
    formaat: str
    taal: str
    bestandsnaam: str
    link: str
    integriteit_algoritme: str
    integriteit_waarde: str
    bestandsomvang: str
    locked: bool

    #TODO: Fix a little better
    @property
    def latest_version(self):
        return self

    def unique_representation(self):
        return f"{self.bronorganisatie} - {self.identificatie}"


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
