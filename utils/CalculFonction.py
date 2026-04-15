from typing import Dict, List

from models.appareil import Appareil


class CalculFonction:
    HEURE_JOUR_DEBUT = 6
    HEURE_JOUR_FIN = 19
    FACTEUR_PANNEAU = 1.40
    FACTEUR_BATTERIE = 1.50

    def _heures_jour(self) -> List[int]:
        return list(range(self.HEURE_JOUR_DEBUT, self.HEURE_JOUR_FIN))

    def _heures_nuit(self) -> List[int]:
        return list(range(self.HEURE_JOUR_FIN, 24)) + list(range(0, self.HEURE_JOUR_DEBUT))

    def charge_horaire(self, appareils: List[Appareil]) -> Dict[int, float]:
        charge = {h: 0.0 for h in range(24)}
        for appareil in appareils:
            for heure in range(24):
                if appareil.est_actif_heure(heure):
                    charge[heure] += appareil.consommation
        return charge

    def estimer(self, appareils: List[Appareil]) -> Dict[str, float]:
        if not appareils:
            return {
                "consommation_24h_wh": 0.0,
                "consommation_jour_wh": 0.0,
                "consommation_nuit_wh": 0.0,
                "puissance_panneau_recommandee_w": 0.0,
                "capacite_batterie_recommandee_wh": 0.0,
                "capacite_batterie_recommandee_ah_12v": 0.0,
                "capacite_batterie_recommandee_ah_24v": 0.0,
                "pic_puissance_jour_w": 0.0,
                "pic_puissance_nuit_w": 0.0,
            }

        charge = self.charge_horaire(appareils)
        heures_jour = self._heures_jour()
        heures_nuit = self._heures_nuit()

        conso_jour_wh = sum(charge[h] for h in heures_jour)
        conso_nuit_wh = sum(charge[h] for h in heures_nuit)
        conso_24h_wh = conso_jour_wh + conso_nuit_wh

        pic_jour_w = max((charge[h] for h in heures_jour), default=0.0)
        pic_nuit_w = max((charge[h] for h in heures_nuit), default=0.0)

        puissance_panneau_base_w = max(pic_jour_w, conso_24h_wh / len(heures_jour))
        puissance_panneau_w = puissance_panneau_base_w * self.FACTEUR_PANNEAU

        capacite_batterie_wh = conso_nuit_wh * self.FACTEUR_BATTERIE

        return {
            "consommation_24h_wh": round(conso_24h_wh, 2),
            "consommation_jour_wh": round(conso_jour_wh, 2),
            "consommation_nuit_wh": round(conso_nuit_wh, 2),
            "puissance_panneau_recommandee_w": round(puissance_panneau_w, 2),
            "capacite_batterie_recommandee_wh": round(capacite_batterie_wh, 2),
            "capacite_batterie_recommandee_ah_12v": round(capacite_batterie_wh / 12 if capacite_batterie_wh else 0.0, 2),
            "capacite_batterie_recommandee_ah_24v": round(capacite_batterie_wh / 24 if capacite_batterie_wh else 0.0, 2),
            "pic_puissance_jour_w": round(pic_jour_w, 2),
            "pic_puissance_nuit_w": round(pic_nuit_w, 2),
        }
