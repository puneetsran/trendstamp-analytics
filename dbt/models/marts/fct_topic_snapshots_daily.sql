-- One row per day: how many topics ran, and how the #1 slot rotated.
-- lag() surfaces whether yesterday's top story carried over to today.
with daily as (
    select
        snapshot_date,
        count(*) as topic_count,
        min(rank) as top_rank,
        max(created_at) as last_topic_created_at
    from {{ ref('stg_topic_snapshots') }}
    group by snapshot_date
),

top_story as (
    select snapshot_date, slug as top_slug, title as top_title
    from {{ ref('stg_topic_snapshots') }}
    where rank = 1
)

select
    daily.snapshot_date,
    daily.topic_count,
    top_story.top_slug,
    top_story.top_title,
    lag(top_story.top_slug) over (order by daily.snapshot_date) as prev_day_top_slug,
    top_story.top_slug = lag(top_story.top_slug) over (order by daily.snapshot_date)
        as top_story_carried_over,
    daily.last_topic_created_at
from daily
left join top_story on top_story.snapshot_date = daily.snapshot_date
order by daily.snapshot_date desc
