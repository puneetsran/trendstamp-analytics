-- One row per (day, topic). Light renaming only — no business logic here.
select
    id as topic_snapshot_id,
    snapshot_date,
    slug,
    rank,
    title,
    summary,
    sources,
    created_at
from {{ source('trendstamp', 'topic_snapshots') }}
