docker cp qualisign.sql qualisign_analysis_postgresdb:qualisign.sql
docker exec qualisign_analysis_postgresdb sh -c "pg_restore -U postgres --schema=public --dbname=postgres --clean qualisign.sql"

pause
