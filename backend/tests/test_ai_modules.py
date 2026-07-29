import os
import pytest
from unittest.mock import AsyncMock, patch
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.api.deps import get_db_session
from app.db.base import Base
from app.main import app

TEST_DB_FILE = "./test_ai_temp.db"
TEST_DATABASE_URL = f"sqlite+aiosqlite:///{TEST_DB_FILE}"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionFactory = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest.fixture(scope="module", autouse=True)
async def setup_test_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db():
    async with TestingSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


app.dependency_overrides[get_db_session] = override_get_db


@pytest.fixture
async def async_client():
    with patch("app.main.check_database_connection", new_callable=AsyncMock) as mock_db_check:
        mock_db_check.return_value = True
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client


@pytest.fixture
async def auth_headers(async_client: AsyncClient):
    reg_payload = {
        "email": "ai.admin@routeai.io",
        "password": "AdminPassword123!",
        "full_name": "AI Systems Admin",
        "role": "ADMIN"
    }
    await async_client.post("/api/v1/auth/register", json=reg_payload)
    login_res = await async_client.post("/api/v1/auth/login", json={"email": "ai.admin@routeai.io", "password": "AdminPassword123!"})
    token = login_res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_predictive_eta_endpoint(async_client: AsyncClient, auth_headers: dict):
    payload = {
        "pickup_lat": 41.8781,
        "pickup_lng": -87.6298,
        "delivery_lat": 41.8900,
        "delivery_lng": -87.6240,
        "traffic_factor": 1.5,
        "weather_condition": "RAIN",
        "stop_service_minutes": 10
    }
    res = await async_client.post("/api/v1/ai/predict-eta", json=payload, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["estimated_distance_km"] > 0
    assert data["traffic_delay_minutes"] > 0
    assert data["weather_delay_minutes"] == 5.0


@pytest.mark.asyncio
async def test_rag_ingestion_and_vector_query_flow(async_client: AsyncClient, auth_headers: dict):
    upload_payload = {
        "title": "Cold Chain Logistics SOP Manual",
        "file_type": "PDF",
        "author": "Compliance Department",
        "content": "Refrigerated cargo vehicles transporting bio-pharmaceuticals must maintain internal temperature strictly between 2C and 8C. Drivers must log temperature telemetry every 15 minutes."
    }
    upload_res = await async_client.post("/api/v1/ai/rag/upload", json=upload_payload, headers=auth_headers)
    assert upload_res.status_code == 201
    assert upload_res.json()["data"]["chunk_count"] >= 1

    query_payload = {
        "query": "What is the required temperature for refrigerated cargo vehicles?",
        "top_k": 2
    }
    query_res = await async_client.post("/api/v1/ai/rag/query", json=query_payload, headers=auth_headers)
    assert query_res.status_code == 200
    results = query_res.json()["data"]
    assert len(results) >= 1
    assert "Cold Chain" in results[0]["document_title"]


@pytest.mark.asyncio
async def test_ai_chat_copilot_endpoint(async_client: AsyncClient, auth_headers: dict):
    chat_payload = {
        "prompt": "How do I optimize delivery routes for urgent orders?",
        "include_rag": True
    }
    res = await async_client.post("/api/v1/ai/chat", json=chat_payload, headers=auth_headers)
    assert res.status_code == 200
    assert "reply" in res.json()["data"]
