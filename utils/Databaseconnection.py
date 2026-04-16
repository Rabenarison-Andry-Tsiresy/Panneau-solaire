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
        database: str = "EnergieSolaire",
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
