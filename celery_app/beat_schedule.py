from celery.schedules import crontab

from app.config import settings

beat_schedule = {
    # Morning orchestration cycle
    "morning-cycle": {
        "task": "celery_app.tasks.daily_cycle.run_morning_cycle",
        "schedule": crontab(hour=settings.morning_cycle_hour, minute=0),
        "options": {"queue": "scheduler"},
    },
    # Evening reporting cycle
    "evening-cycle": {
        "task": "celery_app.tasks.daily_cycle.run_evening_cycle",
        "schedule": crontab(hour=settings.evening_cycle_hour, minute=0),
        "options": {"queue": "scheduler"},
    },
    # Every 2h: check social mentions
    "social-mentions-sweep": {
        "task": "celery_app.tasks.agent_tasks.run_social_sweep",
        "schedule": crontab(minute=0, hour="*/2"),
        "options": {"queue": "agents"},
    },
    # Every 3h: check email inbox
    "email-inbox-sweep": {
        "task": "celery_app.tasks.agent_tasks.run_email_sweep",
        "schedule": crontab(minute=30, hour="*/3"),
        "options": {"queue": "agents"},
    },
    # Every 6h: sync ad metrics + Stripe failed payments
    "ads-stripe-sync": {
        "task": "celery_app.tasks.agent_tasks.run_ads_stripe_sync",
        "schedule": crontab(minute=0, hour="*/6"),
        "options": {"queue": "agents"},
    },
}
