-- Run this ONCE in the Supabase dashboard -> SQL Editor (on trending-now's
-- project), using an admin session. It creates a dedicated low-privilege
-- role for this analytics pipeline instead of using the main postgres
-- superuser or the service_role key.
--
-- Effect: this role can only READ existing production tables, and can only
-- CREATE/WRITE inside a new "analytics" schema. It cannot alter, drop, or
-- write to topic_snapshots / digest_subscribers / topic_follows or any
-- other existing table.

-- Safe to run more than once: only creates the role if it doesn't exist yet.
do $$
begin
  if not exists (select from pg_catalog.pg_roles where rolname = 'dbt_analytics') then
    create role dbt_analytics with login password 'CHANGE_ME_TO_A_GENERATED_PASSWORD';
  end if;
end
$$;

-- Supabase revokes CONNECT-to-database from PUBLIC by default, so a new
-- role can't even log in until it's granted explicitly.
grant connect on database postgres to dbt_analytics;

-- Read-only on existing production tables/views in the public schema.
grant usage on schema public to dbt_analytics;
grant select on all tables in schema public to dbt_analytics;
alter default privileges in schema public grant select on tables to dbt_analytics;

-- Full control, but ONLY inside a new schema this pipeline owns. (No
-- "authorization dbt_analytics" here — Supabase's SQL Editor account can't
-- assume a role it just created, which is what caused the 42501 error.
-- Granting CREATE via "grant all on schema" is enough: any table
-- dbt_analytics creates inside this schema is automatically owned by it.)
create schema if not exists analytics;
grant all on schema analytics to dbt_analytics;
alter default privileges in schema analytics grant all on tables to dbt_analytics;

-- Use these values (not the postgres superuser) in .env:
--   SUPABASE_DB_USER=dbt_analytics
--   SUPABASE_DB_PASSWORD=<the password you set above>
--   SUPABASE_DB_SCHEMA=analytics
