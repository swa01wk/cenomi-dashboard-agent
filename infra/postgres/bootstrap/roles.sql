-- Idempotent role bootstrap (ADR-0006 §3). Passwords are set by `cenomi db init` from the environment.

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'cenomi_owner') THEN
    CREATE ROLE cenomi_owner LOGIN;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'cenomi_seed') THEN
    CREATE ROLE cenomi_seed LOGIN;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'cenomi_reader') THEN
    CREATE ROLE cenomi_reader LOGIN;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'cenomi_app') THEN
    CREATE ROLE cenomi_app LOGIN;
  END IF;
END
$$;

ALTER ROLE cenomi_reader SET default_transaction_read_only = on;
ALTER ROLE cenomi_reader SET statement_timeout = '5000ms';
