"""Test task_service — CRUD and state machine."""
import pytest

from app.services.task_service import (
    create_task,
    get_task,
    get_tasks_today_summary,
    list_tasks,
    update_task_status,
)


@pytest.mark.asyncio
async def test_create_task(async_db_session):
    task = await create_task(
        async_db_session,
        title="Write a blog post",
        agent_type="social_media",
        priority=2,
    )
    await async_db_session.commit()

    assert task.id is not None
    assert task.title == "Write a blog post"
    assert task.status == "pending"
    assert task.priority == 2


@pytest.mark.asyncio
async def test_get_task(async_db_session):
    task = await create_task(async_db_session, title="Find prospects", agent_type="email_outreach")
    await async_db_session.commit()

    fetched = await get_task(async_db_session, task.id)
    assert fetched is not None
    assert fetched.id == task.id


@pytest.mark.asyncio
async def test_get_task_not_found(async_db_session):
    result = await get_task(async_db_session, task_id=99999)
    assert result is None


@pytest.mark.asyncio
async def test_update_task_status(async_db_session):
    task = await create_task(async_db_session, title="Test", agent_type="finance")
    await async_db_session.commit()

    updated = await update_task_status(
        async_db_session, task.id, "completed", result_summary="Done"
    )
    await async_db_session.commit()

    assert updated is not None
    assert updated.status == "completed"
    assert updated.result_summary == "Done"


@pytest.mark.asyncio
async def test_list_tasks_filter_by_status(async_db_session):
    await create_task(async_db_session, title="Task A", agent_type="finance")
    t2 = await create_task(async_db_session, title="Task B", agent_type="social_media")
    await async_db_session.commit()
    await update_task_status(async_db_session, t2.id, "completed")
    await async_db_session.commit()

    pending = await list_tasks(async_db_session, status="pending")
    completed = await list_tasks(async_db_session, status="completed")

    assert all(t.status == "pending" for t in pending)
    assert all(t.status == "completed" for t in completed)
