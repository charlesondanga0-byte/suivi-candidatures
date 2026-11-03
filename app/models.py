from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

Statut = Literal["À envoyer", "Envoyée", "Entretien", "Offre", "Refus"]


class CandidatureIn(BaseModel):
    entreprise: str = Field(min_length=1, max_length=100)
    poste: str = Field(min_length=1, max_length=100)
    lien: Optional[str] = Field(default=None, max_length=500)
    statut: Statut = "À envoyer"
    date_candidature: date = Field(default_factory=date.today)
    notes: Optional[str] = Field(default=None, max_length=2000)

    @field_validator("lien")
    @classmethod
    def lien_http(cls, valeur):
        if valeur is not None and not valeur.lower().startswith(("http://", "https://")):
            raise ValueError("Le lien doit commencer par http:// ou https://")
        return valeur
