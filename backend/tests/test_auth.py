import pytest
from unittest.mock import AsyncMock, patch
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from app.api.deps import get_db_session
from app.db.base import Base
from app.main import app

# Shared in-memory SQLite engine using StaticPool so tables persist across request sessions
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False
)
TestingSessionFactory = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest.fixture(autouse=True)
async def setup_test_database():
    """
    Async fixture initializing in-memory SQLite tables before each test and dropping after.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db():
    """
    FastAPI dependency override yielding in-memory database sessions with automatic commit.
    """
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
    """
    Async HTTP client fixture with mocked database health check during lifespan.
    """
    with patch("app.main.check_database_connection", new_callable=AsyncMock) as mock_db_check:
        mock_db_check.return_value = True
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client


@pytest.mark.asyncio
async def test_user_registration_flow(async_client: AsyncClient):
    """
    Tests user registration endpoint with unique credentials.
    """
    register_payload = {
        "email": "dispatcher.test@routeai.io",
        "password": "Password123!",
        "full_name": "Sarah Connor",
        "role": "DISPATCHER"
    }
    response = await async_client.post("/api/v1/auth/register", json=register_payload)
    assert response.status_code == 201, f"Expected 201 Created, got {response.status_code}: {response.text}"
    
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == "dispatcher.test@routeai.io"
    assert data["data"]["role"] == "DISPATCHER"
    assert "hashed_password" not in data["data"]


@pytest.mark.asyncio
async def test_user_registration_duplicate_email(async_client: AsyncClient):
    """
    Tests duplicate email registration rejection.
    """
    register_payload = {
        "email": "dispatcher.duplicate@routeai.io",
        "password": "Password123!",
        "full_name": "Sarah Connor",
        "role": "DISPATCHER"
    }
    # 1. Register first user
    res1 = await async_client.post("/api/v1/auth/register", json=register_payload)
    assert res1.status_code == 201

    # 2. Attempt duplicate registration
    res2 = await async_client.post("/api/v1/auth/register", json=register_payload)
    assert res2.status_code == 422
    data = res2.json()
    assert data["success"] is False
    assert data["error"]["code"] == "VALIDATION_FAILED"


@pytest.mark.asyncio
async def test_user_login_and_me_profile_flow(async_client: AsyncClient):
    """
    Tests user login authentication, JWT token generation, and /me profile retrieval.
    """
    # 1. Register user
    register_payload = {
        "email": "driver.john@routeai.io",
        "password": "DriverPassword123!",
        "full_name": "John Driver",
        "role": "DRIVER"
    }
    reg_res = await async_client.post("/api/v1/auth/register", json=register_payload)
    assert reg_res.status_code == 201

    # 2. Login with valid credentials
    login_payload = {
        "email": "driver.john@routeai.io",
        "password": "DriverPassword123!"
    }
    login_res = await async_client.post("/api/v1/auth/login", json=login_payload)
    assert login_res.status_code == 200, f"Expected 200 OK, got {login_res.status_code}: {login_res.text}"
    
    token_data = login_res.json()["data"]
    access_token = token_data["access_token"]
    assert access_token is not None
    assert token_data["token_type"] == "bearer"

    # 3. Fetch /me profile using Bearer token header
    headers = {"Authorization": f"Bearer {access_token}"}
    me_res = await async_client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    profile = me_res.json()["data"]
    assert profile["email"] == "driver.john@routeai.io"
    assert profile["role"] == "DRIVER"


@pytest.mark.asyncio
async def test_role_based_access_control(async_client: AsyncClient):
    """
    Tests RBAC authorization restrictions on /admin-only endpoint.
    """
    # 1. Register an ADMIN user
    admin_payload = {
        "email": "admin.system@routeai.io",
        "password": "AdminPassword123!",
        "full_name": "System Administrator",
        "role": "ADMIN"
    }
    reg_admin = await async_client.post("/api/v1/auth/register", json=admin_payload)
    assert reg_admin.status_code == 201

    # 2. Register a DRIVER user
    driver_payload = {
        "email": "driver.dave@routeai.io",
        "password": "DavePassword123!",
        "full_name": "Dave Driver",
        "role": "DRIVER"
    }
    reg_driver = await async_client.post("/api/v1/auth/register", json=driver_payload)
    assert reg_driver.status_code == 201

    # 3. Login as ADMIN
    admin_login = await async_client.post("/api/v1/auth/login", json={"email": "admin.system@routeai.io", "password": "AdminPassword123!"})
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["data"]["access_token"]

    # 4. Login as DRIVER
    driver_login = await async_client.post("/api/v1/auth/login", json={"email": "driver.dave@routeai.io", "password": "DavePassword123!"})
    assert driver_login.status_code == 200
    driver_token = driver_login.json()["data"]["access_token"]

    # 5. Access /admin-only as ADMIN -> Success HTTP 200
    admin_res = await async_client.get("/api/v1/auth/admin-only", headers={"Authorization": f"Bearer {admin_token}"})
    assert admin_res.status_code == 200
    assert admin_res.json()["data"]["access_granted"] is True

    # 6. Access /admin-only as DRIVER -> Forbidden HTTP 403
    driver_res = await async_client.get("/api/v1/auth/admin-only", headers={"Authorization": f"Bearer {driver_token}"})
    assert driver_res.status_code == 403
    assert driver_res.json()["error"]["code"] == "AUTHORIZATION_FAILED"
