"""Test memory_service — dual-write to PG + ChromaDB."""
import pytest

from app.services.memory_service import list_memories, search_memory, store_memory


@pytest.mark.asyncio
async def test_store_memory_creates_pg_record(async_db_session, mock_chroma):
    entry = await store_memory(
        async_db_session,
        category="strategy",
        title="Growth lever identified",
        content="Referral program drives 30% of sign-ups at competitors",
        source="competitor_research",
        tags=["growth", "referral"],
    )
    await async_db_session.commit()

    assert entry.id is not None
    assert entry.category == "strategy"
    assert entry.chroma_id is not None


@pytest.mark.asyncio
async def test_store_memory_calls_chroma(async_db_session, mock_chroma):
    await store_memory(
        async_db_session,
        category="competitor",
        title="Competitor pricing",
        content="Acme charges $99/mo for the starter plan",
    )

    mock_chroma.add.assert_called_once()
    call_kwargs = mock_chroma.add.call_args[1]
    assert "Acme charges" in call_kwargs["documents"][0]


@pytest.mark.asyncio
async def test_search_memory_returns_results(async_db_session, mock_chroma):
    results = await search_memory(async_db_session, "referral growth", n_results=5)

    assert isinstance(results, list)
    assert len(results) > 0
    assert "content" in results[0]


@pytest.mark.asyncio
async def test_list_memories_filters_by_category(async_db_session, mock_chroma):
    await store_memory(async_db_session, category="strategy", title="S1", content="c1")
    await store_memory(async_db_session, category="competitor", title="C1", content="c2")
    await async_db_session.commit()

    strategy = await list_memories(async_db_session, category="strategy")
    assert all(m.category == "strategy" for m in strategy)
