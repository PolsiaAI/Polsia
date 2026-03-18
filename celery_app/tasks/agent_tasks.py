"""Per-agent Celery tasks — dispatched by the orchestrator or Beat."""
import asyncio
import time

from celery_app.worker import app


def _run_sync(coro):
    """Run an async coroutine from a sync Celery task."""
    return asyncio.get_event_loop().run_until_complete(coro)


@app.task(name="celery_app.tasks.agent_tasks.run_agent_task", bind=True, max_retries=2)
def run_agent_task(self, task_id: int):
    """Load a Task from DB, build context, run the correct agent, save result."""
    import asyncio

    async def _execute():
        from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
        from app.config import settings
        from app.agents.crew_factory import run_agent_for_task
        from app.services.task_service import get_task, update_task_status, create_agent_run, finish_agent_run
        from app.services.company_service import get_full_context
        from app.services.activity_service import log_activity

        engine = create_async_engine(settings.database_url)
        Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with Session() as db:
            task = await get_task(db, task_id)
            if not task:
                return

            await update_task_status(db, task_id, "in_progress")
            context = await get_full_context(db)
            run = await create_agent_run(db, task.agent_type, task_id=task_id, input_context=context)
            await db.commit()

        start = time.monotonic()
        try:
            task_dict = {"id": task.id, "title": task.title, "description": task.description}
            result = run_agent_for_task(task.agent_type, task_dict, context)
            status = "completed"
            summary = result.get("summary", "Task completed.")
            error = None
        except Exception as exc:
            status = "failed"
            summary = None
            error = str(exc)
            result = {}

        duration = round(time.monotonic() - start, 2)

        async with Session() as db:
            await update_task_status(db, task_id, status, result_summary=summary, error_message=error)
            await finish_agent_run(db, run.id, status, output=result, duration_secs=duration)
            await log_activity(
                db,
                agent_type=task.agent_type,
                action="task_completed" if status == "completed" else "task_failed",
                summary=summary or error or "No output",
                level="success" if status == "completed" else "error",
            )
            await db.commit()

        await engine.dispose()

    asyncio.run(_execute())


@app.task(name="celery_app.tasks.agent_tasks.run_social_sweep")
def run_social_sweep():
    """Sweep social mentions every 2h."""
    from celery_app.tasks.agent_tasks import run_agent_task
    run_agent_task.delay_with_id = None  # placeholder — create task then enqueue
    _create_and_run("social_media", "Check social mentions and reply to engaging comments")


@app.task(name="celery_app.tasks.agent_tasks.run_email_sweep")
def run_email_sweep():
    _create_and_run("customer_support", "Check inbox and reply to customer emails")


@app.task(name="celery_app.tasks.agent_tasks.run_ads_stripe_sync")
def run_ads_stripe_sync():
    _create_and_run("ads_management", "Sync ad metrics from Google and Meta")
    _create_and_run("finance", "Check for failed Stripe payments and update revenue snapshot")


def _create_and_run(agent_type: str, title: str):
    async def _inner():
        from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
        from app.config import settings
        from app.services.task_service import create_task

        engine = create_async_engine(settings.database_url)
        Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with Session() as db:
            task = await create_task(db, title=title, agent_type=agent_type, source="scheduler")
            await db.commit()
            task_id = task.id

        await engine.dispose()
        return task_id

    task_id = asyncio.run(_inner())
    run_agent_task.delay(task_id)
