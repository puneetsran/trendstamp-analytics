-- Run this ONCE in the Supabase dashboard -> SQL Editor (on trending-now's
-- project), using an admin session. It creates a dedicated low-privilege
-- role for this analytics pipeline instead of using the main postgres
-- superuser or the service_role key.
--
-- Effect: this role can only READ existing production tables, and can only
-- CREATE/WRITE inside a new "analytics" schema. It cannot alter, drop, or
-- write to topic_snapshots / digest_subscribers / topic_follows or any
-- other existing table.

create role dbt_analytics with login password 'CHANGE_ME_TO_A_GENERATED_PASSWORD';

-- Read-only on existing production tables/views in the public schema.
grant usage on schema public to dbt_analytics;
grant select on all tables in schema public to dbt_analytics;
alter default privileges in schema public grant select on tables to dbt_analytics;

-- Full control, but ONLY inside a new schema this pipeline owns.
create schema if not exists analytics authorization dbt_analytics;
grant all on schema analytics to dbt_analytics;
alter default privileges in schema analytics grant all on tables to dbt_analytics;

-- Use these values (not the postgres superuser) in .env:
--   SUPABASE_DB_USER=dbt_analytics
--   SUPABASE_DB_PASSWORD=<the password you set above>
--   SUPABASE_DB_SCHEMA=analytics
