select
    id as follow_id,
    user_id,
    topic_title,
    slug,
    keywords,
    created_at as followed_at
from {{ source('trendstamp', 'topic_follows') }}
