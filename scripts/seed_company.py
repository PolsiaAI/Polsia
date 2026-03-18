"""Seed a default CompanyConfig row if none exists."""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.config import settings
from app.models.company import CompanyConfig


async def seed():
    engine = create_async_engine(settings.database_url)
    Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with Session() as session:
        result = await session.execute(select(CompanyConfig).limit(1))
        existing = result.scalar_one_or_none()

        if existing:
            print("Company config already exists — skipping seed.")
            return

        company = CompanyConfig(
            name="My Company",
            mission="Build products that make people's lives better.",
            vision="Become the go-to solution in our market within 3 years.",
            description="A SaaS platform that automates key business operations.",
            target_market="Small and medium-sized businesses in North America.",
            value_prop="Save 10+ hours per week by automating your marketing, sales, and support.",
            pricing_model={"plans": [{"name": "Starter", "price": 49}, {"name": "Pro", "price": 149}]},
            goals={"q1_2026": ["Hit $10K MRR", "Get 100 paying customers", "Launch v2 of product"]},
            kpis={
                "mrr_usd": 0,
                "active_customers": 0,
                "churn_rate": 0.0,
                "cac_usd": 0,
                "ltv_usd": 0,
                "nps": 0,
            },
            website_url="https://yourcompany.com",
            github_repo="yourorg/yourrepo",
            product_type="SaaS",
            industry="Technology",
            timezone="UTC",
            daily_cycle_hour=6,
        )
        session.add(company)
        await session.commit()
        print(f"Seeded company: {company.name}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
