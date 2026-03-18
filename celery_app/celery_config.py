from app.config import settings

broker_url = settings.celery_broker_url
result_backend = settings.celery_result_backend

task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]
timezone = "UTC"
enable_utc = True

# Worker settings
worker_prefetch_multiplier = 1
task_acks_late = True
task_reject_on_worker_lost = True

# Routing
task_routes = {
    "celery_app.tasks.daily_cycle.*": {"queue": "scheduler"},
    "celery_app.tasks.agent_tasks.*": {"queue": "agents"},
    "celery_app.tasks.maintenance.*": {"queue": "maintenance"},
}

# Result backend settings
result_expires = 86400  # 24h
