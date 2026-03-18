"""Morning and evening cycle Celery tasks — triggered by Beat."""
import asyncio

from celery_app.worker import app


@app.task(name="celery_app.tasks.daily_cycle.run_morning_cycle")
def run_morning_cycle():
    """06:00 UTC — Finance snapshot + Orchestrator morning plan."""
    async def _inner():
        from datetime import date
        from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
        from app.config import settings
        from app.services.company_service import get_full_context
        from app.services.task_service import create_task
        from app.services.activity_service import log_activity
        from app.agents.crew_factory import run_agent_for_task

        engine = create_async_engine(settings.database_url)
        Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with Session() as db:
            # 1. Finance snapshot
            finance_task = await create_task(
                db,
                title="Daily revenue snapshot",
                agent_type="finance",
                source="scheduler",
                priority=1,
            )
            await db.commit()

        # Run finance snapshot synchronously before orchestrator
        from celery_app.tasks.agent_tasks import run_agent_task
        run_agent_task.apply(args=[finance_task.id])  # synchronous apply

        async with Session() as db:
            context = await get_full_context(db)

            # 2. Orchestrator morning plan
            orch_task_dict = {
                "title": "Morning planning cycle",
                "description": f"Generate today's task plan for {date.today()}",
            }
            result = run_agent_for_task("orchestrator", orch_task_dict, context)

            await log_activity(
                db,
                agent_type="orchestrator",
                action="morning_plan_complete",
                summary=result.get("summary", "Morning plan generated"),
                level="success",
            )
            await db.commit()

        # 3. Always-run agents
        for agent_type, title in [
            ("customer_support", "Morning customer support sweep"),
            ("social_media", "Morning social media check"),
        ]:
            async with Session() as db:
                t = await create_task(db, title=title, agent_type=agent_type, source="scheduler", priority=2)
                await db.commit()
                run_agent_task.delay(t.id)

        await engine.dispose()

    asyncio.run(_inner())


@app.task(name="celery_app.tasks.daily_cycle.run_evening_cycle")
def run_evening_cycle():
    """20:00 UTC — Finance P&L + Orchestrator evening summary."""
    async def _inner():
        from datetime import date
        from sqlalchemy import func, select
        from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
        from app.config import settings
        from app.models.task import Task
        from app.services.company_service import get_full_context
        from app.services.task_service import create_task
        from app.services.report_service import save_evening_summary
        from app.services.activity_service import log_activity
        from app.agents.crew_factory import run_agent_for_task

        engine = create_async_engine(settings.database_url)
        Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with Session() as db:
            context = await get_full_context(db)

            # Count today's task outcomes
            from datetime import datetime
            today_start = datetime.combine(date.today(), datetime.min.time())
            completed = await db.execute(
                select(func.count(Task.id)).where(
                    Task.created_at >= today_start, Task.status == "completed"
                )
            )
            failed = await db.execute(
                select(func.count(Task.id)).where(
                    Task.created_at >= today_start, Task.status == "failed"
                )
            )

            orch_task_dict = {
                "title": "Evening reporting cycle",
                "description": f"Generate evening summary for {date.today()}",
            }
            result = run_agent_for_task("orchestrator", orch_task_dict, context)

            await save_evening_summary(
                db,
                report_date=date.today(),
                summary=result.get("summary", "Evening summary generated"),
                insights=result.get("insights", []),
                tasks_completed=completed.scalar() or 0,
                tasks_failed=failed.scalar() or 0,
                metrics_snapshot=context.get("kpis", {}),
            )

            await log_activity(
                db,
                agent_type="orchestrator",
                action="evening_summary_complete",
                summary=result.get("summary", "Evening summary complete"),
                level="success",
            )
            await db.commit()

        await engine.dispose()

    asyncio.run(_inner())
