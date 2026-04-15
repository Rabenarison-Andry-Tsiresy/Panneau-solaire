from pathlib import Path
from typing import List, Optional, Tuple

from models.appareil import Appareil

try:
    import mysql.connector
except Exception:
    mysql = None


class DatabaseConnection:
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 3306,
        user: str = "root",
        password: str = "",
        database: str = "Energie-Solaire",
    ) -> None:
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

    def _is_available(self) -> bool:
        return mysql is not None and hasattr(mysql, "connector")

    def connect(self):
        if not self._is_available():
            raise RuntimeError("mysql-connector-python n'est pas installé")

        return mysql.connector.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            autocommit=True,
        )

    def execute_sql_file(self, sql_file: Path) -> Tuple[bool, str]:
        try:
            sql_text = sql_file.read_text(encoding="utf-8")
            commands = [c.strip() for c in sql_text.split(";") if c.strip()]

            with self.connect() as conn:
                with conn.cursor() as cursor:
                    for command in commands:
                        cursor.execute(command)
            return True, "Script SQL exécuté avec succès"
        except Exception as exc:
            return False, f"Erreur SQL: {exc}"

    def charger_appareils(self) -> Tuple[List[Appareil], Optional[str]]:
        try:
            query = """
                SELECT a.nom, u.heure_debut, u.heure_fin, a.consommation
                FROM appareil_usage u
                JOIN appareil a ON a.id_appareil = u.id_appareil
                ORDER BY u.id_appareil_usage
            """

            appareils: List[Appareil] = []
            with self.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    for nom, heure_debut, heure_fin, consommation in cursor.fetchall():
                        hd = int(str(heure_debut).split(":")[0])
                        hf = int(str(heure_fin).split(":")[0])
                        appareils.append(
                            Appareil(
                                nom=nom,
                                heure_debut=hd,
                                heure_fin=hf,
                                consommation=float(consommation),
                            )
                        )

            return appareils, None
        except Exception as exc:
            return [], f"Connexion/lecture DB impossible: {exc}"

    def sauvegarder_appareils(self, appareils: List[Appareil]) -> Tuple[bool, str]:
        try:
            with self.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM appareil_usage")
                    cursor.execute("DELETE FROM appareil")

                    for appareil in appareils:
                        cursor.execute(
                            "INSERT INTO appareil (nom, consommation) VALUES (%s, %s)",
                            (appareil.nom, appareil.consommation),
                        )
                        id_appareil = cursor.lastrowid
                        cursor.execute(
                            """
                            INSERT INTO appareil_usage (id_appareil, heure_debut, heure_fin)
                            VALUES (%s, %s, %s)
                            """,
                            (id_appareil, f"{appareil.heure_debut:02d}:00:00", f"{appareil.heure_fin:02d}:00:00"),
                        )
            return True, "Sauvegarde DB effectuée"
        except Exception as exc:
            return False, f"Sauvegarde DB impossible: {exc}"
