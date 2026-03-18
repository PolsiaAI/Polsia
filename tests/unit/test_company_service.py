"""Test company_service — get_full_context and build_context_prompt."""
import pytest

from app.models.company import CompanyConfig
from app.services.company_service import build_context_prompt, get_full_context


@pytest.mark.asyncio
async def test_get_full_context_empty_db(async_db_session):
    result = await get_full_context(async_db_session)
    assert result == {}


@pytest.mark.asyncio
async def test_get_full_context_with_company(async_db_session):
    company = CompanyConfig(
        name="Test Co",
        mission="Make testing great",
        kpis={"mrr_usd": 1000},
    )
    async_db_session.add(company)
    await async_db_session.commit()

    result = await get_full_context(async_db_session)

    assert result["company"]["name"] == "Test Co"
    assert result["kpis"]["mrr_usd"] == 1000


def test_build_context_prompt_empty():
    result = build_context_prompt({})
    assert "No company context" in result


def test_build_context_prompt_with_data():
    context = {
        "company": {"name": "ACME", "mission": "Be great", "description": "A company"},
        "kpis": {"mrr_usd": 5000},
        "yesterday_summary": "Good day",
        "todays_tasks": [{"title": "Do thing", "agent_type": "social_media", "status": "pending"}],
    }
    result = build_context_prompt(context)
    assert "ACME" in result
    assert "mrr_usd" in result
    assert "Good day" in result
    assert "Do thing" in result
