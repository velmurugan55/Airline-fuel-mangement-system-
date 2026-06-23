"""
Integration Tests — Auth and full fuel transaction flow.
Uses an isolated SQLite database per test session with table teardown between tests.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from application.app import app
from application.providers.database import get_db, Base
from application.repositories.user_repository import UserRepository
from application.src.models.user_model import UserRole

# ── In-memory SQLite for tests ────────────────────────────────────────────────
SQLITE_URL = "sqlite:///./test_fuel.db"
engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def reset_db():
    """
    Drop and recreate all tables before each test to ensure full isolation.
    This prevents 409/state-leakage between tests sharing the same file DB.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Always seed a test user
    db = TestingSessionLocal()
    try:
        repo = UserRepository(db)
        repo.create_user("testadmin", "testpass123", role=UserRole.admin)
    finally:
        db.close()

    yield  # run the test

    # teardown (optional — next setup already drops tables)


client = TestClient(app)


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_auth_token() -> str:
    response = client.post(
        "/auth/login",
        data={"username": "testadmin", "password": "testpass123"},
    )
    assert response.status_code == 200, f"Login failed: {response.json()}"
    return response.json()["access_token"]


def auth_headers() -> dict:
    return {"Authorization": f"Bearer {get_auth_token()}"}


def create_airline(headers: dict) -> dict:
    resp = client.post(
        "/airlines",
        json={
            "airline_code": "GA",
            "airline_name": "Garuda Indonesia",
            "contact_person": "John Doe",
            "email": "ops@garuda.com",
            "phone": "+62-21-0000",
            "address": "Jakarta",
        },
        headers=headers,
    )
    assert resp.status_code == 201, resp.json()
    return resp.json()


def create_vendor(headers: dict) -> dict:
    resp = client.post(
        "/vendors",
        json={
            "vendor_code": "PT-FUEL",
            "vendor_name": "PT Pertamina",
            "contact_person": "Jane",
            "email": "fuel@pertamina.com",
            "phone": "+62-21-1111",
            "address": "Jakarta",
        },
        headers=headers,
    )
    assert resp.status_code == 201, resp.json()
    return resp.json()


def set_fuel_price(headers: dict, vendor_id: int, price: float = 12500.0) -> dict:
    resp = client.post(
        "/fuel-prices",
        json={
            "vendor_id": vendor_id,
            "price_per_liter": price,
            "effective_date": "2024-06-01",
        },
        headers=headers,
    )
    assert resp.status_code == 201, resp.json()
    return resp.json()


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_health_check():
    """GET /health returns 200 with status=healthy."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_login_success():
    """Valid credentials return a bearer token."""
    response = client.post(
        "/auth/login",
        data={"username": "testadmin", "password": "testpass123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["username"] == "testadmin"


def test_login_wrong_password():
    """Wrong password returns 401."""
    response = client.post(
        "/auth/login",
        data={"username": "testadmin", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_protected_endpoint_without_token():
    """Accessing a protected endpoint without a token returns 401."""
    response = client.get("/airlines")
    assert response.status_code == 401


def test_create_airline():
    """POST /airlines creates an airline and returns 201."""
    headers = auth_headers()
    data = create_airline(headers)
    assert data["airline_code"] == "GA"
    assert data["airline_name"] == "Garuda Indonesia"
    assert "id" in data


def test_duplicate_airline_code_returns_409():
    """Creating two airlines with the same code returns 409 Conflict."""
    headers = auth_headers()
    create_airline(headers)
    # Second call — same code
    resp = client.post(
        "/airlines",
        json={"airline_code": "GA", "airline_name": "Another Airline"},
        headers=headers,
    )
    assert resp.status_code == 409


def test_get_airline_by_id():
    """GET /airlines/{id} returns the correct airline."""
    headers = auth_headers()
    airline = create_airline(headers)
    resp = client.get(f"/airlines/{airline['id']}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["airline_code"] == "GA"


def test_get_airline_not_found():
    """GET /airlines/9999 returns 404."""
    headers = auth_headers()
    resp = client.get("/airlines/9999", headers=headers)
    assert resp.status_code == 404


def test_update_airline():
    """PUT /airlines/{id} updates airline fields."""
    headers = auth_headers()
    airline = create_airline(headers)
    resp = client.put(
        f"/airlines/{airline['id']}",
        json={"email": "new@garuda.com"},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["email"] == "new@garuda.com"


def test_delete_airline():
    """DELETE /airlines/{id} removes the airline."""
    headers = auth_headers()
    airline = create_airline(headers)
    del_resp = client.delete(f"/airlines/{airline['id']}", headers=headers)
    assert del_resp.status_code == 200
    # Confirm gone
    get_resp = client.get(f"/airlines/{airline['id']}", headers=headers)
    assert get_resp.status_code == 404


def test_create_vendor():
    """POST /vendors creates a vendor and returns 201."""
    headers = auth_headers()
    data = create_vendor(headers)
    assert data["vendor_code"] == "PT-FUEL"
    assert "id" in data


def test_fuel_price_history():
    """GET /fuel-prices/history/{vendor_id} returns all prices for vendor."""
    headers = auth_headers()
    vendor = create_vendor(headers)
    set_fuel_price(headers, vendor["id"], 12000.0)
    set_fuel_price(headers, vendor["id"], 12500.0)

    resp = client.get(f"/fuel-prices/history/{vendor['id']}", headers=headers)
    assert resp.status_code == 200
    history = resp.json()["history"]
    assert len(history) == 2
    # newest first
    assert float(history[0]["price_per_liter"]) == 12500.0


def test_get_latest_fuel_price():
    """GET /fuel-prices/latest/{vendor_id} returns the most recent price."""
    headers = auth_headers()
    vendor = create_vendor(headers)
    set_fuel_price(headers, vendor["id"], 11000.0)
    set_fuel_price(headers, vendor["id"], 13500.0)  # latest

    resp = client.get(f"/fuel-prices/latest/{vendor['id']}", headers=headers)
    assert resp.status_code == 200
    assert float(resp.json()["price_per_liter"]) == 13500.0


def test_transaction_blocked_without_fuel_price():
    """
    Business Rule #5: Creating a transaction when no fuel price exists
    must return HTTP 422.
    """
    headers = auth_headers()
    airline = create_airline(headers)
    vendor = create_vendor(headers)
    # Intentionally skip setting a fuel price

    response = client.post(
        "/transactions",
        json={
            "airline_id": airline["id"],
            "vendor_id": vendor["id"],
            "fuel_quantity": 1000.0,
            "transaction_date": "2024-06-22",
        },
        headers=headers,
    )
    assert response.status_code == 422


def test_full_transaction_happy_path():
    """
    Full happy path:
      set fuel price → create transaction → verify invoice calculation → fetch invoice.
    """
    headers = auth_headers()
    airline = create_airline(headers)
    vendor = create_vendor(headers)
    set_fuel_price(headers, vendor["id"], 12500.0)

    # Create transaction
    txn_resp = client.post(
        "/transactions",
        json={
            "airline_id": airline["id"],
            "vendor_id": vendor["id"],
            "fuel_quantity": 1000.0,
            "transaction_date": "2024-06-22",
            "remarks": "Test refuel",
        },
        headers=headers,
    )
    assert txn_resp.status_code == 201
    txn = txn_resp.json()

    # Verify business rules #3 and #4
    assert txn["invoice_no"].startswith("INV-20240622-")  # Rule #3
    assert float(txn["fuel_price"]) == 12500.0             # Rule #2 auto-select
    assert float(txn["total_amount"]) == 1000.0 * 12500.0  # Rule #4

    # Fetch the full invoice
    inv_resp = client.get(f"/transactions/{txn['invoice_no']}", headers=headers)
    assert inv_resp.status_code == 200
    inv = inv_resp.json()
    assert inv["invoice_no"] == txn["invoice_no"]
    assert inv["airline"]["airline_code"] == "GA"
    assert inv["vendor"]["vendor_code"] == "PT-FUEL"
    assert inv["total_amount"] == 1000.0 * 12500.0


def test_invoice_sequence_increments():
    """
    Business Rule #3: Multiple transactions on the same date should produce
    incrementing invoice numbers (INV-YYYYMMDD-0001, -0002, ...).
    """
    headers = auth_headers()
    airline = create_airline(headers)
    vendor = create_vendor(headers)
    set_fuel_price(headers, vendor["id"])

    payload = {
        "airline_id": airline["id"],
        "vendor_id": vendor["id"],
        "fuel_quantity": 100.0,
        "transaction_date": "2024-06-22",
    }
    r1 = client.post("/transactions", json=payload, headers=headers)
    r2 = client.post("/transactions", json=payload, headers=headers)
    assert r1.status_code == 201
    assert r2.status_code == 201
    assert r1.json()["invoice_no"] == "INV-20240622-0001"
    assert r2.json()["invoice_no"] == "INV-20240622-0002"


def test_dashboard_report():
    """GET /reports/dashboard returns KPI metrics."""
    headers = auth_headers()
    airline = create_airline(headers)
    vendor = create_vendor(headers)
    set_fuel_price(headers, vendor["id"])

    client.post(
        "/transactions",
        json={
            "airline_id": airline["id"],
            "vendor_id": vendor["id"],
            "fuel_quantity": 500.0,
            "transaction_date": "2024-06-22",
        },
        headers=headers,
    )

    resp = client.get("/reports/dashboard", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_transactions"] == 1
    assert float(data["total_fuel_quantity"]) == 500.0
    assert len(data["top_airlines"]) == 1
    assert len(data["top_vendors"]) == 1


def test_invoice_report_with_filter():
    """GET /reports/invoices with date filter returns correct records."""
    headers = auth_headers()
    airline = create_airline(headers)
    vendor = create_vendor(headers)
    set_fuel_price(headers, vendor["id"])

    client.post(
        "/transactions",
        json={
            "airline_id": airline["id"],
            "vendor_id": vendor["id"],
            "fuel_quantity": 200.0,
            "transaction_date": "2024-06-22",
        },
        headers=headers,
    )

    # Filter within range — should return 1
    resp = client.get(
        "/reports/invoices?from_date=2024-06-01&to_date=2024-06-30",
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["total_records"] == 1

    # Filter outside range — should return 0
    resp2 = client.get(
        "/reports/invoices?from_date=2024-07-01&to_date=2024-07-31",
        headers=headers,
    )
    assert resp2.status_code == 200
    assert resp2.json()["total_records"] == 0
