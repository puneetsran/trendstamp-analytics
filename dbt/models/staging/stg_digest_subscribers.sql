select
    id as subscriber_id,
    email,
    source as signup_source,
    user_id,
    created_at as signed_up_at
from {{ source('trendstamp', 'digest_subscribers') }}
