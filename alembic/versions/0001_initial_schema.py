"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-03-02
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "company_config",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("mission", sa.Text()),
        sa.Column("vision", sa.Text()),
        sa.Column("description", sa.Text()),
        sa.Column("target_market", sa.Text()),
        sa.Column("value_prop", sa.Text()),
        sa.Column("pricing_model", postgresql.JSONB()),
        sa.Column("goals", postgresql.JSONB()),
        sa.Column("kpis", postgresql.JSONB()),
        sa.Column("website_url", sa.String(512)),
        sa.Column("github_repo", sa.String(512)),
        sa.Column("product_type", sa.String(100)),
        sa.Column("industry", sa.String(100)),
        sa.Column("timezone", sa.String(50), server_default="UTC"),
        sa.Column("daily_cycle_hour", sa.Integer(), server_default="6"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("agent_type", sa.String(100), nullable=False),
        sa.Column("priority", sa.Integer(), server_default="3"),
        sa.Column("status", sa.String(50), server_default="pending"),
        sa.Column("source", sa.String(100), server_default="orchestrator"),
        sa.Column("scheduled_date", sa.DateTime(timezone=True)),
        sa.Column("result_summary", sa.Text()),
        sa.Column("error_message", sa.Text()),
        sa.Column("metadata", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "agent_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("task_id", sa.Integer(), sa.ForeignKey("tasks.id")),
        sa.Column("agent_type", sa.String(100), nullable=False),
        sa.Column("run_type", sa.String(100), server_default="task"),
        sa.Column("status", sa.String(50), server_default="running"),
        sa.Column("input_context", postgresql.JSONB()),
        sa.Column("output", postgresql.JSONB()),
        sa.Column("raw_log", sa.Text()),
        sa.Column("tokens_used", sa.Integer()),
        sa.Column("cost_usd", sa.Float()),
        sa.Column("duration_secs", sa.Float()),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("ended_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "activity_log",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("agent_type", sa.String(100), nullable=False),
        sa.Column("action", sa.String(255), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("detail", postgresql.JSONB()),
        sa.Column("level", sa.String(20), server_default="info"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "memory_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("source", sa.String(100)),
        sa.Column("tags", postgresql.ARRAY(sa.String())),
        sa.Column("chroma_id", sa.String(255), unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "social_posts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("platform", sa.String(50), server_default="twitter"),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("status", sa.String(50), server_default="draft"),
        sa.Column("tweet_id", sa.String(100)),
        sa.Column("scheduled_for", sa.DateTime(timezone=True)),
        sa.Column("published_at", sa.DateTime(timezone=True)),
        sa.Column("engagement", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "social_engagements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("mention_id", sa.String(100), unique=True),
        sa.Column("author_handle", sa.String(100)),
        sa.Column("content", sa.Text()),
        sa.Column("our_reply", sa.Text()),
        sa.Column("reply_id", sa.String(100)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "prospects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("first_name", sa.String(100)),
        sa.Column("last_name", sa.String(100)),
        sa.Column("company", sa.String(255)),
        sa.Column("title", sa.String(255)),
        sa.Column("source", sa.String(100)),
        sa.Column("status", sa.String(50), server_default="new"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "email_campaigns",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("goal", sa.Text()),
        sa.Column("target_segment", sa.String(255)),
        sa.Column("status", sa.String(50), server_default="active"),
        sa.Column("total_sent", sa.Integer(), server_default="0"),
        sa.Column("total_opened", sa.Integer(), server_default="0"),
        sa.Column("total_replied", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "email_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("prospect_id", sa.Integer(), sa.ForeignKey("prospects.id"), nullable=False),
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("email_campaigns.id")),
        sa.Column("sequence_step", sa.Integer(), server_default="1"),
        sa.Column("subject", sa.String(512)),
        sa.Column("body", sa.Text()),
        sa.Column("sendgrid_id", sa.String(255)),
        sa.Column("status", sa.String(50), server_default="sent"),
        sa.Column("sent_at", sa.DateTime(timezone=True)),
        sa.Column("opened_at", sa.DateTime(timezone=True)),
        sa.Column("replied_at", sa.DateTime(timezone=True)),
        sa.Column("follow_up_due", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "ad_campaigns",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("platform", sa.String(50), nullable=False),
        sa.Column("external_id", sa.String(255)),
        sa.Column("name", sa.String(512), nullable=False),
        sa.Column("goal", sa.String(255)),
        sa.Column("status", sa.String(50), server_default="active"),
        sa.Column("daily_budget_usd", sa.Float(), server_default="0"),
        sa.Column("total_spent_usd", sa.Float(), server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "ad_metrics",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("ad_campaigns.id"), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("impressions", sa.Integer(), server_default="0"),
        sa.Column("clicks", sa.Integer(), server_default="0"),
        sa.Column("conversions", sa.Integer(), server_default="0"),
        sa.Column("spend_usd", sa.Float(), server_default="0"),
        sa.Column("ctr", sa.Float(), server_default="0"),
        sa.Column("cpc", sa.Float(), server_default="0"),
        sa.Column("roas", sa.Float(), server_default="0"),
    )

    op.create_table(
        "competitors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("website", sa.String(512)),
        sa.Column("pricing_info", postgresql.JSONB()),
        sa.Column("positioning", sa.Text()),
        sa.Column("strengths", postgresql.ARRAY(sa.String())),
        sa.Column("weaknesses", postgresql.ARRAY(sa.String())),
        sa.Column("last_researched", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "stripe_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("stripe_event_id", sa.String(255), unique=True, nullable=False),
        sa.Column("event_type", sa.String(255), nullable=False),
        sa.Column("customer_id", sa.String(255)),
        sa.Column("amount_cents", sa.Integer()),
        sa.Column("currency", sa.String(10)),
        sa.Column("status", sa.String(50), server_default="processed"),
        sa.Column("raw_payload", postgresql.JSONB()),
        sa.Column("processed_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "revenue_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("snapshot_date", sa.Date(), unique=True, nullable=False),
        sa.Column("mrr_cents", sa.Integer(), server_default="0"),
        sa.Column("arr_cents", sa.Integer(), server_default="0"),
        sa.Column("active_subscribers", sa.Integer(), server_default="0"),
        sa.Column("churned_today", sa.Integer(), server_default="0"),
        sa.Column("new_today", sa.Integer(), server_default="0"),
        sa.Column("total_revenue_month_cents", sa.Integer(), server_default="0"),
        sa.Column("stripe_balance_cents", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "expense_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("vendor", sa.String(255), nullable=False),
        sa.Column("amount_cents", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(10), server_default="usd"),
        sa.Column("description", sa.Text()),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("external_ref", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "daily_reports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("report_date", sa.Date(), unique=True, nullable=False),
        sa.Column("morning_plan", sa.Text()),
        sa.Column("evening_summary", sa.Text()),
        sa.Column("tasks_planned", sa.Integer(), server_default="0"),
        sa.Column("tasks_completed", sa.Integer(), server_default="0"),
        sa.Column("tasks_failed", sa.Integer(), server_default="0"),
        sa.Column("metrics_snapshot", postgresql.JSONB()),
        sa.Column("insights", postgresql.ARRAY(sa.String())),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Useful indexes
    op.create_index("ix_tasks_status", "tasks", ["status"])
    op.create_index("ix_tasks_agent_type", "tasks", ["agent_type"])
    op.create_index("ix_activity_log_created_at", "activity_log", ["created_at"])
    op.create_index("ix_activity_log_agent_type", "activity_log", ["agent_type"])
    op.create_index("ix_memory_entries_category", "memory_entries", ["category"])
    op.create_index("ix_stripe_events_event_type", "stripe_events", ["event_type"])
    op.create_index("ix_revenue_snapshots_date", "revenue_snapshots", ["snapshot_date"])


def downgrade() -> None:
    for table in [
        "daily_reports", "expense_records", "revenue_snapshots", "stripe_events",
        "competitors", "ad_metrics", "ad_campaigns", "email_logs", "email_campaigns",
        "prospects", "social_engagements", "social_posts", "memory_entries",
        "activity_log", "agent_runs", "tasks", "company_config",
    ]:
        op.drop_table(table)
