docker exec postgresql_postgresdb_1 sh -c "pg_dump -Fc -U postgres --schema=public --data-only postgres --file=qualisign.sql"
docker cp postgresql_postgresdb_1:qualisign.sql qualisign.sql

pause
