docker cp qualisign.sql postgresql_postgresdb_1:qualisign.sql
docker exec postgresql_postgresdb_1 sh -c "pg_restore -U postgres --schema=public --dbname=postgres --clean qualisign.sql"

pause
