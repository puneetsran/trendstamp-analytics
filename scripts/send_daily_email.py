"""Reads the latest mart-table rollups and emails a daily summary via Resend.

Run after `dbt run` so the mart tables are fresh — see
.github/workflows/daily-email.yml for the scheduled version.
"""
import os

import psycopg2
import psycopg2.extras
import resend


def fetch_latest_rollups(cur):
    cur.execute(
        """
        select snapshot_date, topic_count, top_slug, top_title,
               top_story_carried_over
        from fct_topic_snapshots_daily
        order by snapshot_date desc
        limit 1
        """
    )
    topics = cur.fetchone()

    cur.execute(
        """
        select signup_date, new_signups, new_signups_signed_in,
               new_signups_anonymous, cumulative_signups
        from fct_digest_signups_daily
        order by signup_date desc
        limit 1
        """
    )
    signups = cur.fetchone()

    return topics, signups


def build_email_html(topics, signups):
    carried_over = "yes" if topics["top_story_carried_over"] else "no"
    return f"""
    <h2>trendstamp daily rollup — {topics['snapshot_date']}</h2>
    <h3>Topics</h3>
    <ul>
      <li>Topics tracked: {topics['topic_count']}</li>
      <li>Top story: {topics['top_title']} ({topics['top_slug']})</li>
      <li>Carried over from previous day: {carried_over}</li>
    </ul>
    <h3>Digest signups — {signups['signup_date']}</h3>
    <ul>
      <li>New signups: {signups['new_signups']}
          ({signups['new_signups_signed_in']} signed-in,
          {signups['new_signups_anonymous']} anonymous)</li>
      <li>Cumulative signups: {signups['cumulative_signups']}</li>
    </ul>
    """


def main():
    conn = psycopg2.connect(
        host=os.environ["SUPABASE_DB_HOST"],
        port=os.environ.get("SUPABASE_DB_PORT", "5432"),
        user=os.environ.get("SUPABASE_DB_USER", "postgres"),
        password=os.environ["SUPABASE_DB_PASSWORD"],
        dbname=os.environ.get("SUPABASE_DB_NAME", "postgres"),
        options=f"-c search_path={os.environ.get('SUPABASE_DB_SCHEMA', 'analytics')}",
        sslmode="require",
    )
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            topics, signups = fetch_latest_rollups(cur)
    finally:
        conn.close()

    resend.api_key = os.environ["RESEND_API_KEY"]
    resend.Emails.send({
        "from": os.environ["DAILY_EMAIL_FROM"],
        "to": os.environ["DAILY_EMAIL_TO"],
        "subject": f"trendstamp daily rollup — {topics['snapshot_date']}",
        "html": build_email_html(topics, signups),
    })


if __name__ == "__main__":
    main()
