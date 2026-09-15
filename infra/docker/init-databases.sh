#!/bin/sh
set -eu
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres <<'SQL'
\getenv app_password APP_DATABASE_PASSWORD
\getenv reader_password WAREHOUSE_PASSWORD
\getenv loader_password WAREHOUSE_LOADER_PASSWORD
CREATE ROLE analystos_app LOGIN PASSWORD :'app_password';
CREATE ROLE analystos_loader LOGIN PASSWORD :'loader_password';
CREATE ROLE analystos_reader LOGIN PASSWORD :'reader_password';
CREATE DATABASE analystos_app OWNER analystos_app;
CREATE DATABASE demo_warehouse OWNER analystos_loader;
REVOKE ALL ON DATABASE analystos_app FROM PUBLIC;
REVOKE ALL ON DATABASE demo_warehouse FROM PUBLIC;
GRANT CONNECT ON DATABASE demo_warehouse TO analystos_reader;
ALTER ROLE analystos_reader SET default_transaction_read_only = on;
ALTER ROLE analystos_reader SET statement_timeout = '30s';
ALTER ROLE analystos_reader SET search_path = marts;
\connect demo_warehouse
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
SET ROLE analystos_loader;
CREATE SCHEMA raw;
CREATE SCHEMA staging;
CREATE SCHEMA intermediate;
CREATE SCHEMA marts;
GRANT USAGE ON SCHEMA marts TO analystos_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA marts GRANT SELECT ON TABLES TO analystos_reader;
ALTER DEFAULT PRIVILEGES REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;
RESET ROLE;
\connect analystos_app
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
SQL

