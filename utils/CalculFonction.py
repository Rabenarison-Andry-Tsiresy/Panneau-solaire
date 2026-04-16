from typing import Dict, List, Optional, Tuple

from models.appareil import Appareil
from models.configuration import ConfigurationCalcul


class CalculFonction:
    def __init__(self, configuration: Optional[ConfigurationCalcul] = None):
        self.configuration = configuration or ConfigurationCalcul()

    def _plage(self, debut: int, fin: int) -> List[Tuple[int, int]]:
        secondes_par_jour = self.configuration.secondes_par_jour
        if debut < fin:
            return [(debut, fin)]
        if debut > fin:
            return [(debut, secondes_par_jour), (0, fin)]
        return [(0, secondes_par_jour)]

    def _plage_panneau_fort(self) -> List[Tuple[int, int]]:
        return self._plage(self.configuration.panneau_fort_debut_s, self.configuration.panneau_fort_fin_s)

    def _plage_panneau_faible(self) -> List[Tuple[int, int]]:
        return self._plage(self.configuration.panneau_faible_debut_s, self.configuration.panneau_faible_fin_s)

    def _plage_batterie(self) -> List[Tuple[int, int]]:
        return self._plage(self.configuration.batterie_debut_s, self.configuration.batterie_fin_s)

    @staticmethod
    def _intersection(debut_a: int, fin_a: int, debut_b: int, fin_b: int) -> int:
        return max(0, min(fin_a, fin_b) - max(debut_a, debut_b))

    def _energie_sur_plage_wh(self, appareils: List[Appareil], plage: List[Tuple[int, int]]) -> float:
        energie_totale_wh = 0.0
        for appareil in appareils:
            for actif_debut, actif_fin in appareil.intervalles_actifs_journee():
                for plage_debut, plage_fin in plage:
                    secondes_communes = self._intersection(actif_debut, actif_fin, plage_debut, plage_fin)
                    if secondes_communes > 0:
                        energie_totale_wh += appareil.consommation * (secondes_communes / 3600.0)
        return energie_totale_wh

    @staticmethod
    def _duree_plages_heures(plages: List[Tuple[int, int]]) -> float:
        return sum((fin - debut) / 3600.0 for debut, fin in plages)

    def _duree_recharge_batterie_heures(self, plages_jour: List[Tuple[int, int]]) -> float:
        duree_configuree = self.configuration.duree_recharge_batterie_heures
        if duree_configuree and duree_configuree > 0:
            return duree_configuree
        return self._duree_plages_heures(plages_jour)

    def _pic_sur_plage_w(self, appareils: List[Appareil], plage: List[Tuple[int, int]]) -> float:
        pic = 0.0
        for plage_debut, plage_fin in plage:
            evenements: List[Tuple[int, int, float]] = []
            for appareil in appareils:
                for actif_debut, actif_fin in appareil.intervalles_actifs_journee():
                    debut = max(plage_debut, actif_debut)
                    fin = min(plage_fin, actif_fin)
                    if debut < fin:
                        evenements.append((debut, 1, appareil.consommation))
                        evenements.append((fin, 0, appareil.consommation))

            if not evenements:
                continue

            evenements.sort(key=lambda e: (e[0], e[1]))
            charge_courante = 0.0
            i = 0
            while i < len(evenements):
                temps = evenements[i][0]
                while i < len(evenements) and evenements[i][0] == temps and evenements[i][1] == 0:
                    charge_courante -= evenements[i][2]
                    i += 1
                while i < len(evenements) and evenements[i][0] == temps and evenements[i][1] == 1:
                    charge_courante += evenements[i][2]
                    i += 1
                if charge_courante > pic:
                    pic = charge_courante
        return pic

    def estimer(self, appareils: List[Appareil]) -> Dict[str, float]:
        if not appareils:
            return {
                "consommation_24h_wh": 0.0,
                "puissance_panneau_recommandee_w": 0.0,
                "capacite_batterie_recommandee_wh": 0.0,
            }

        # Regle:
        # - Jour: le panneau alimente les appareils + recharge la batterie.
        # - Nuit: la batterie alimente les appareils.
        plage_panneau_40 = self._plage_panneau_fort()
        plage_panneau_20 = self._plage_panneau_faible()
        plage_batterie_19_6 = self._plage_batterie()
        plages_jour = plage_panneau_40 + plage_panneau_20

        energie_panneau_6_17_wh = self._energie_sur_plage_wh(appareils, plage_panneau_40)
        energie_panneau_17_19_wh = self._energie_sur_plage_wh(appareils, plage_panneau_20)
        energie_batterie_19_6_wh = self._energie_sur_plage_wh(appareils, plage_batterie_19_6)
        energie_totale_24h_wh = energie_panneau_6_17_wh + energie_panneau_17_19_wh + energie_batterie_19_6_wh

        pic_charge_6_17_w = self._pic_sur_plage_w(appareils, plage_panneau_40)
        pic_charge_17_19_w = self._pic_sur_plage_w(appareils, plage_panneau_20)

        # Nouveau mecanisme d'approximation:
        # Recharge batterie continue pendant la journee,
        # P_recharge = E_nuit / t_recharge
        duree_recharge_h = self._duree_recharge_batterie_heures(plages_jour)
        puissance_recharge_batterie_w = (
            energie_batterie_19_6_wh / duree_recharge_h if duree_recharge_h > 0 else 0.0
        )

        if self.configuration.recharge_continue_en_journee:
            puissance_panneau_min_pour_pic_w = max(
                (
                    (pic_charge_6_17_w + puissance_recharge_batterie_w) / self.configuration.facteur_panneau_fort
                    if self.configuration.facteur_panneau_fort
                    else 0.0
                ),
                (
                    (pic_charge_17_19_w + puissance_recharge_batterie_w) / self.configuration.facteur_panneau_faible
                    if self.configuration.facteur_panneau_faible
                    else 0.0
                ),
            )
        else:
            puissance_panneau_min_pour_pic_w = max(
                (
                    pic_charge_6_17_w / self.configuration.facteur_panneau_fort
                    if self.configuration.facteur_panneau_fort
                    else 0.0
                ),
                (
                    pic_charge_17_19_w / self.configuration.facteur_panneau_faible
                    if self.configuration.facteur_panneau_faible
                    else 0.0
                ),
            )

        heures_6_17 = self._duree_plages_heures(plage_panneau_40)
        heures_17_19 = self._duree_plages_heures(plage_panneau_20)
        heures_solaires_equivalentes = (
            heures_6_17 * self.configuration.facteur_panneau_fort
            + heures_17_19 * self.configuration.facteur_panneau_faible
        )

        # Formule electrique de base: E = P * t.
        # Le panneau fournit les charges de jour + la recharge batterie pour la nuit.
        energie_charges_jour_wh = energie_panneau_6_17_wh + energie_panneau_17_19_wh
        energie_recharge_batterie_wh = energie_batterie_19_6_wh
        energie_a_fournir_par_panneau_wh = energie_charges_jour_wh + energie_recharge_batterie_wh
        puissance_panneau_min_pour_energie_w = (
            energie_a_fournir_par_panneau_wh / heures_solaires_equivalentes if heures_solaires_equivalentes else 0.0
        )

        # Proposition panneau sans marge supplementaire.
        puissance_panneau_recommandee_w = max(puissance_panneau_min_pour_pic_w, puissance_panneau_min_pour_energie_w)

        # Batterie: on n'utilise que 50% de la capacite nominale.
        capacite_batterie_nominale_wh = (
            (
                energie_batterie_19_6_wh / self.configuration.fraction_batterie_utilisable
                if self.configuration.fraction_batterie_utilisable
                else 0.0
            )
        )
        # Proposition batterie: +50% sur la capacite calculee.
        capacite_batterie_recommandee_wh = (
            capacite_batterie_nominale_wh * self.configuration.marge_proposition_batterie
        )

        return {
            "consommation_24h_wh": round(energie_totale_24h_wh, 2),
            "puissance_panneau_recommandee_w": round(puissance_panneau_recommandee_w, 2),
            "capacite_batterie_recommandee_wh": round(capacite_batterie_recommandee_wh, 2),
        }
