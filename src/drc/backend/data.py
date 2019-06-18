from dataclasses import dataclass
from datetime import date


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
