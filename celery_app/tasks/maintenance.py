"""Maintenance tasks — cleanup, health checks, etc."""
from celery_app.worker import app


@app.task(name="celery_app.tasks.maintenance.cleanup_old_activity")
def cleanup_old_activity():
    """Delete activity_log entries older than 90 days."""
    import asyncio
    from datetime import datetime, timedelta

    async def _inner():
        from sqlalchemy import delete
        from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
        from app.config import settings
        from app.models.report import ActivityLog

        engine = create_async_engine(settings.database_url)
        Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        cutoff = datetime.utcnow() - timedelta(days=90)
        async with Session() as db:
            await db.execute(delete(ActivityLog).where(ActivityLog.created_at < cutoff))
            await db.commit()

        await engine.dispose()

    asyncio.run(_inner())
