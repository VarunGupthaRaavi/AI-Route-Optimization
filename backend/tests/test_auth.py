import os
import pytest
from unittest.mock import AsyncMock, patch
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.api.deps import get_db_session
from app.db.base import Base
from app.main import app

TEST_DB_FILE = "./test_auth_temp.db"
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


@pytest.mark.asyncio
async def test_user_registration_flow(async_client: AsyncClient):
    register_payload = {
        "email": "dispatcher.test@routeai.io",
        "password": "Password123!",
        "full_name": "Sarah Connor",
        "role": "DISPATCHER"
    }
    response = await async_client.post("/api/v1/auth/register", json=register_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == "dispatcher.test@routeai.io"


@pytest.mark.asyncio
async def test_user_registration_duplicate_email(async_client: AsyncClient):
    register_payload = {
        "email": "dispatcher.duplicate@routeai.io",
        "password": "Password123!",
        "full_name": "Sarah Connor",
        "role": "DISPATCHER"
    }
    res1 = await async_client.post("/api/v1/auth/register", json=register_payload)
    assert res1.status_code == 201

    res2 = await async_client.post("/api/v1/auth/register", json=register_payload)
    assert res2.status_code == 422


@pytest.mark.asyncio
async def test_user_login_and_me_profile_flow(async_client: AsyncClient):
    register_payload = {
        "email": "driver.john@routeai.io",
        "password": "DriverPassword123!",
        "full_name": "John Driver",
        "role": "DRIVER"
    }
    await async_client.post("/api/v1/auth/register", json=register_payload)

    login_res = await async_client.post("/api/v1/auth/login", json={"email": "driver.john@routeai.io", "password": "DriverPassword123!"})
    assert login_res.status_code == 200
    token = login_res.json()["data"]["access_token"]

    me_res = await async_client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["data"]["email"] == "driver.john@routeai.io"


@pytest.mark.asyncio
async def test_role_based_access_control(async_client: AsyncClient):
    admin_payload = {
        "email": "admin.system@routeai.io",
        "password": "AdminPassword123!",
        "full_name": "System Administrator",
        "role": "ADMIN"
    }
    await async_client.post("/api/v1/auth/register", json=admin_payload)

    driver_payload = {
        "email": "driver.dave@routeai.io",
        "password": "DavePassword123!",
        "full_name": "Dave Driver",
        "role": "DRIVER"
    }
    await async_client.post("/api/v1/auth/register", json=driver_payload)

    admin_login = await async_client.post("/api/v1/auth/login", json={"email": "admin.system@routeai.io", "password": "AdminPassword123!"})
    admin_token = admin_login.json()["data"]["access_token"]

    driver_login = await async_client.post("/api/v1/auth/login", json={"email": "driver.dave@routeai.io", "password": "DavePassword123!"})
    driver_token = driver_login.json()["data"]["access_token"]

    admin_res = await async_client.get("/api/v1/auth/admin-only", headers={"Authorization": f"Bearer {admin_token}"})
    assert admin_res.status_code == 200

    driver_res = await async_client.get("/api/v1/auth/admin-only", headers={"Authorization": f"Bearer {driver_token}"})
    assert driver_res.status_code == 403
