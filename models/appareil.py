from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class Appareil:
    nom: str
    heure_debut: int  # secondes depuis minuit
    heure_fin: int  # secondes depuis minuit
    consommation: float  # Watts

    SECONDES_PAR_JOUR = 24 * 3600

    @staticmethod
    def parse_hms(texte: str) -> int:
        valeur = texte.strip()
        morceaux = valeur.split(":")
        if len(morceaux) != 3:
            raise ValueError("Le format d'heure doit etre HH:MM:SS")

        try:
            heures = int(morceaux[0])
            minutes = int(morceaux[1])
            secondes = int(morceaux[2])
        except Exception as exc:
            raise ValueError("Le format d'heure doit etre HH:MM:SS") from exc

        if not (0 <= heures <= 23 and 0 <= minutes <= 59 and 0 <= secondes <= 59):
            raise ValueError("Heure invalide: HH[0-23], MM[0-59], SS[0-59]")

        return heures * 3600 + minutes * 60 + secondes

    @staticmethod
    def format_hms(secondes_total: int) -> str:
        secondes = int(secondes_total) % Appareil.SECONDES_PAR_JOUR
        heures = secondes // 3600
        minutes = (secondes % 3600) // 60
        sec = secondes % 60
        return f"{heures:02d}:{minutes:02d}:{sec:02d}"

    def intervalles_actifs_journee(self) -> List[Tuple[int, int]]:
        if self.heure_debut == self.heure_fin:
            return [(0, self.SECONDES_PAR_JOUR)]
        if self.heure_debut < self.heure_fin:
            return [(self.heure_debut, self.heure_fin)]
        return [(self.heure_debut, self.SECONDES_PAR_JOUR), (0, self.heure_fin)]

    @classmethod
    def requete_selection(cls) -> str:
        return """
            SELECT a.nom, u.heure_debut, u.heure_fin, a.consommation
            FROM appareil_usage u
            JOIN appareil a ON a.id_appareil = u.id_appareil
            ORDER BY u.id_appareil_usage
        """

    @classmethod
    def requete_insert_appareil(cls) -> str:
        return "INSERT INTO appareil (nom, consommation) VALUES (%s, %s)"

    @classmethod
    def requete_insert_usage(cls) -> str:
        return """
            INSERT INTO appareil_usage (id_appareil, heure_debut, heure_fin)
            VALUES (%s, %s, %s)
        """

    @classmethod
    def requete_supprimer_usage(cls) -> str:
        return "DELETE FROM appareil_usage"

    @classmethod
    def requete_supprimer_appareils(cls) -> str:
        return "DELETE FROM appareil"

    @classmethod
    def from_db_row(cls, nom: str, heure_debut, heure_fin, consommation) -> "Appareil":
        hd = cls.parse_hms(str(heure_debut))
        hf = cls.parse_hms(str(heure_fin))
        return cls(
            nom=str(nom),
            heure_debut=hd,
            heure_fin=hf,
            consommation=float(consommation),
        )

    def to_db_insert_appareil_params(self) -> Tuple[str, float]:
        return self.nom, self.consommation

    def to_db_insert_usage_params(self, id_appareil: int) -> Tuple[int, str, str]:
        return id_appareil, self.format_hms(self.heure_debut), self.format_hms(self.heure_fin)

    @classmethod
    def charger_depuis_db(cls, db) -> Tuple[List["Appareil"], Optional[str]]:
        try:
            appareils: List[Appareil] = []
            with db.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(cls.requete_selection())
                    for nom, heure_debut, heure_fin, consommation in cursor.fetchall():
                        appareils.append(cls.from_db_row(nom, heure_debut, heure_fin, consommation))
            return appareils, None
        except Exception as exc:
            return [], f"Connexion/lecture DB impossible: {exc}"

    @classmethod
    def sauvegarder_dans_db(cls, db, appareils: List["Appareil"]) -> Tuple[bool, str]:
        try:
            with db.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(cls.requete_supprimer_usage())
                    cursor.execute(cls.requete_supprimer_appareils())

                    for appareil in appareils:
                        cursor.execute(cls.requete_insert_appareil(), appareil.to_db_insert_appareil_params())
                        id_appareil = cursor.lastrowid
                        cursor.execute(cls.requete_insert_usage(), appareil.to_db_insert_usage_params(id_appareil))
            return True, "Sauvegarde DB effectuée"
        except Exception as exc:
            return False, f"Sauvegarde DB impossible: {exc}"
    
    def est_actif_heure(self, heure: int) -> bool:
        debut_heure = heure * 3600
        fin_heure = ((heure + 1) % 24) * 3600

        for debut, fin in self.intervalles_actifs_journee():
            if fin_heure == 0:
                if max(debut, debut_heure) < min(fin, self.SECONDES_PAR_JOUR):
                    return True
            else:
                if max(debut, debut_heure) < min(fin, fin_heure):
                    return True
        return False
