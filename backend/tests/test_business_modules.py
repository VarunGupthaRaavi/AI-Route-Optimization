import os
import pytest
from unittest.mock import AsyncMock, patch
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.api.deps import get_db_session
from app.db.base import Base
from app.main import app

TEST_DB_FILE = "./test_biz_temp.db"
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
        "email": "admin.biz@routeai.io",
        "password": "AdminPassword123!",
        "full_name": "Business Admin",
        "role": "ADMIN"
    }
    await async_client.post("/api/v1/auth/register", json=reg_payload)
    login_res = await async_client.post("/api/v1/auth/login", json={"email": "admin.biz@routeai.io", "password": "AdminPassword123!"})
    token = login_res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_business_modules_e2e_flow(async_client: AsyncClient, auth_headers: dict):
    # 1. Customer CRUD
    cust_payload = {
        "name": "Acme Logistics Corp",
        "company_name": "Acme Corp",
        "email": "shipments@acme.com",
        "phone": "+1-555-0199",
        "address": "100 Warehouse Way, Chicago, IL",
        "latitude": 41.8781,
        "longitude": -87.6298
    }
    cust_res = await async_client.post("/api/v1/customers", json=cust_payload, headers=auth_headers)
    assert cust_res.status_code == 201
    cust_id = cust_res.json()["data"]["id"]

    cust_list = await async_client.get("/api/v1/customers?q=Acme", headers=auth_headers)
    assert cust_list.status_code == 200
    assert cust_list.json()["data"]["total"] >= 1

    # 2. Vehicle CRUD
    veh_payload = {
        "license_plate": "IL-ROUTE-99",
        "vehicle_model": "Ford Transit Cargo Van",
        "capacity_kg": 1500.0,
        "volume_m3": 12.5,
        "fuel_type": "DIESEL",
        "max_range_km": 650.0
    }
    veh_res = await async_client.post("/api/v1/vehicles", json=veh_payload, headers=auth_headers)
    assert veh_res.status_code == 201
    veh_id = veh_res.json()["data"]["id"]

    # 3. Driver CRUD
    driv_payload = {
        "license_number": "CDL-99887766",
        "phone": "+1-555-0144",
        "assigned_vehicle_id": veh_id
    }
    driv_res = await async_client.post("/api/v1/drivers", json=driv_payload, headers=auth_headers)
    assert driv_res.status_code == 201
    driv_id = driv_res.json()["data"]["id"]

    # 4. Delivery Orders & Scheduling
    deliv1_payload = {
        "customer_id": cust_id,
        "pickup_address": "Hub Depot, Chicago, IL",
        "delivery_address": "250 Michigan Ave, Chicago, IL",
        "pickup_lat": 41.8781,
        "pickup_lng": -87.6298,
        "delivery_lat": 41.8900,
        "delivery_lng": -87.6240,
        "weight_kg": 120.0,
        "priority": "HIGH"
    }
    del1_res = await async_client.post("/api/v1/deliveries", json=deliv1_payload, headers=auth_headers)
    assert del1_res.status_code == 201
    deliv1_id = del1_res.json()["data"]["id"]

    deliv2_payload = {
        "customer_id": cust_id,
        "pickup_address": "Hub Depot, Chicago, IL",
        "delivery_address": "500 W Madison St, Chicago, IL",
        "pickup_lat": 41.8781,
        "pickup_lng": -87.6298,
        "delivery_lat": 41.8820,
        "delivery_lng": -87.6400,
        "weight_kg": 85.0,
        "priority": "URGENT"
    }
    del2_res = await async_client.post("/api/v1/deliveries", json=deliv2_payload, headers=auth_headers)
    assert del2_res.status_code == 201
    deliv2_id = del2_res.json()["data"]["id"]

    # 5. AI Route Optimization Trigger
    opt_payload = {
        "delivery_ids": [deliv1_id, deliv2_id],
        "vehicle_id": veh_id
    }
    opt_res = await async_client.post("/api/v1/routes/optimize", json=opt_payload, headers=auth_headers)
    assert opt_res.status_code == 201
    route_data = opt_res.json()["data"]
    route_id = route_data["id"]
    assert route_data["status"] == "OPTIMIZED"
    assert len(route_data["stops"]) == 2

    # 6. Driver & Vehicle Allocation
    alloc_res = await async_client.post(f"/api/v1/routes/{route_id}/allocate-driver", json={"driver_id": driv_id, "vehicle_id": veh_id}, headers=auth_headers)
    assert alloc_res.status_code == 200
    assert alloc_res.json()["data"]["status"] == "IN_PROGRESS"

    # 7. Notifications Feed & Read Status
    notif_list = await async_client.get("/api/v1/notifications", headers=auth_headers)
    assert notif_list.status_code == 200

    # 8. Executive Dashboard Analytics
    analytics_res = await async_client.get("/api/v1/analytics/dashboard", headers=auth_headers)
    assert analytics_res.status_code == 200
    summary = analytics_res.json()["data"]
    assert summary["total_customers"] >= 1
    assert summary["total_vehicles"] >= 1
    assert summary["total_drivers"] >= 1
    assert summary["total_deliveries"] >= 2
    assert summary["total_routes"] >= 1
