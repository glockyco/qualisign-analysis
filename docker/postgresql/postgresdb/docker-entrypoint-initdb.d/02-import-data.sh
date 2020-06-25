pg_restore -U postgres --schema=public --dbname=postgres --clean /docker-entrypoint-initdb.d/02-import-data.dump
