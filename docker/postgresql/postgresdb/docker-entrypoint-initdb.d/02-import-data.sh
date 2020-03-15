pg_restore -U postgres --schema=public --dbname=postgres --clean /docker-entrypoint-initdb.d/11-import-data.dump
