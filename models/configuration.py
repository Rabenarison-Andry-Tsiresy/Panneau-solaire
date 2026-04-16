from dataclasses import dataclass


@dataclass(frozen=True)
class ConfigurationCalcul:
    """Configuration centrale du dimensionnement (facilement modifiable)."""

    panneau_fort_debut_hms: str = "06:00:00"
    panneau_fort_fin_hms: str = "17:00:00"
    panneau_faible_debut_hms: str = "17:00:00"
    panneau_faible_fin_hms: str = "19:00:00"
    batterie_debut_hms: str = "19:00:00"
    batterie_fin_hms: str = "06:00:00"

    facteur_panneau_fort: float = 0.40
    facteur_panneau_faible: float = 0.20

    fraction_batterie_utilisable: float = 0.50
    marge_proposition_batterie: float = 0.75

    # Nouveau mecanisme:
    # Si True, la recharge batterie est supposee continue sur toute la plage panneau.
    recharge_continue_en_journee: bool = True
    # Permet de forcer une duree de recharge specifique (en heures), sinon calculee automatiquement.
    duree_recharge_batterie_heures: float = 0.0

    secondes_par_jour: int = 24 * 3600

    @staticmethod
    def _hms_vers_secondes(hms: str) -> int:
        morceaux = hms.split(":")
        if len(morceaux) != 3:
            raise ValueError("Le format d'heure doit etre HH:MM:SS")

        heures = int(morceaux[0])
        minutes = int(morceaux[1])
        secondes = int(morceaux[2])

        if not (0 <= heures <= 23 and 0 <= minutes <= 59 and 0 <= secondes <= 59):
            raise ValueError("Heure invalide: HH[0-23], MM[0-59], SS[0-59]")

        return heures * 3600 + minutes * 60 + secondes

    @property
    def panneau_fort_debut_s(self) -> int:
        return self._hms_vers_secondes(self.panneau_fort_debut_hms)

    @property
    def panneau_fort_fin_s(self) -> int:
        return self._hms_vers_secondes(self.panneau_fort_fin_hms)

    @property
    def panneau_faible_debut_s(self) -> int:
        return self._hms_vers_secondes(self.panneau_faible_debut_hms)

    @property
    def panneau_faible_fin_s(self) -> int:
        return self._hms_vers_secondes(self.panneau_faible_fin_hms)

    @property
    def batterie_debut_s(self) -> int:
        return self._hms_vers_secondes(self.batterie_debut_hms)

    @property
    def batterie_fin_s(self) -> int:
        return self._hms_vers_secondes(self.batterie_fin_hms)
