-- Daily new-signup count plus a running cumulative total, split by
-- anonymous vs. signed-in-user signups (drawer opt-in vs. archive box).
with daily as (
    select
        date_trunc('day', signed_up_at)::date as signup_date,
        count(*) as new_signups,
        count(*) filter (where user_id is not null) as new_signups_signed_in,
        count(*) filter (where user_id is null) as new_signups_anonymous
    from {{ ref('stg_digest_subscribers') }}
    group by 1
)

select
    signup_date,
    new_signups,
    new_signups_signed_in,
    new_signups_anonymous,
    sum(new_signups) over (order by signup_date) as cumulative_signups
from daily
order by signup_date desc
