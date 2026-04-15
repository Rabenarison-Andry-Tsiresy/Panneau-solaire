from dataclasses import dataclass


@dataclass
class Appareil:
    nom: str
    heure_debut: int
    heure_fin: int
    consommation: float  # Watts

    def est_actif_heure(self, heure: int) -> bool:
        if self.heure_debut == self.heure_fin:
            return True
        if self.heure_debut < self.heure_fin:
            return self.heure_debut <= heure < self.heure_fin
        return heure >= self.heure_debut or heure < self.heure_fin
