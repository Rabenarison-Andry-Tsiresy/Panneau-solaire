

# 1. Copie ton fichier .sql dans le conteneur
docker cp ./data/init.sql monserver-sql:/tmp/init.sql

# 2. Connecte-toi au conteneur et exécute-le
docker exec -it monserver-sql  bash

cd /opt/mssql-tools18/bin/

./sqlcmd -S localhost -U sa -P 'Shadow2024' -i /tmp/init2.sql -C