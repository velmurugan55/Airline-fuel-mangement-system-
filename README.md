# ✈️ Airline Fuel Management System

A **production-ready** backend for airline fuel operations built with **FastAPI**, **PostgreSQL**, **SQLAlchemy**, **Alembic**, and **JWT Authentication** following **Clean Architecture** principles.

---

## 📁 Project Structure

```
fuel-system/
│
├── application/
│   ├── controllers/api/          # FastAPI routers (HTTP layer)
│   │   ├── auth_controller.py
│   │   ├── airline_controller.py
│   │   ├── vendor_controller.py
│   │   ├── fuel_price_controller.py
│   │   ├── transaction_controller.py
│   │   ├── report_controller.py
│   │   └── dependencies.py       # JWT guard + role check
│   │
│   ├── dto/                      # Pydantic request/response schemas
│   │   ├── airline_dto.py
│   │   ├── vendor_dto.py
│   │   ├── fuel_price_dto.py
│   │   ├── transaction_dto.py
│   │   └── report_dto.py
│   │
│   ├── entities/                 # Pure domain objects (decoupled from ORM)
│   │   ├── airline.py
│   │   ├── vendor.py
│   │   ├── fuel_price.py
│   │   ├── transaction.py
│   │   └── user.py
│   │
│   ├── repositories/             # Data access layer
│   │   ├── ibase.py
│   │   ├── airline_repository.py
│   │   ├── vendor_repository.py
│   │   ├── fuel_price_repository.py
│   │   ├── transaction_repository.py
│   │   └── user_repository.py
│   │
│   ├── usecases/                 # Business logic layer
│   │   ├── airline_usecase.py
│   │   ├── vendor_usecase.py
│   │   ├── fuel_price_usecase.py
│   │   ├── transaction_usecase.py
│   │   └── report_usecase.py
│   │
│   ├── providers/                # Infrastructure services
│   │   ├── database.py           # SQLAlchemy engine + session
│   │   ├── jwt_provider.py       # Token creation & validation
│   │   └── invoice_provider.py   # Invoice number generation
│   │
│   ├── exception/
│   │   ├── custom_exception.py
│   │   └── not_found_exception.py
│   │
│   ├── src/models/               # SQLAlchemy ORM models
│   │   ├── user_model.py
│   │   ├── airline_model.py
│   │   ├── vendor_model.py
│   │   ├── fuel_price_model.py
│   │   └── transaction_model.py
│   │
│   ├── app.py                    # FastAPI app factory
│   └── config.py                 # Pydantic settings
│
├── migrations/                   # Alembic migration scripts
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│
├── tests/
│   └── test_auth_and_flow.py
│
├── seed.py                       # Default user seeder
├── requirements.txt
├── .env
├── alembic.ini
└── README.md
```

---

## ⚙️ Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.11+ |
| PostgreSQL | 14+ |
| pip | latest |

---

## 🚀 Quick Start

### 1. Clone / Open the Project

```bash
cd "fuel-system"
```

### 2. Create & Activate Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Edit `.env` with your actual PostgreSQL credentials:

```env
PROJECT_NAME="Airline Fuel Management System"
ENVIRONMENT=development
DEBUG=True

POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=fuel_system

DATABASE_URL=postgresql+psycopg2://postgres:your_password@localhost:5432/fuel_system

SECRET_KEY=your-very-long-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 5. Create the PostgreSQL Database

```sql
-- Run in psql or pgAdmin
CREATE DATABASE fuel_system;
```

### 6. Run Database Migrations

```bash
# Generate the initial migration (auto-detects all models)
alembic revision --autogenerate -m "initial_schema"

# Apply migrations to the database
alembic upgrade head
```

### 7. Seed Default Users

```bash
python seed.py
```

This creates:
| Username | Password | Role |
|---|---|---|
| `admin` | `admin123` | admin |
| `operator` | `operator123` | operator |

> ⚠️ **Change passwords immediately in production!**

### 8. Run the Server

```bash
uvicorn application.app:app --reload --host 0.0.0.0 --port 8000
```

---

## 📖 API Documentation

Once the server is running, visit:

| Interface | URL |
|---|---|
| **Swagger UI** | http://localhost:8000/docs |
| **ReDoc** | http://localhost:8000/redoc |
| **OpenAPI JSON** | http://localhost:8000/openapi.json |
| **Health Check** | http://localhost:8000/health |

---

## 🔐 Authentication

All endpoints (except `/auth/login` and `/health`) require a **JWT Bearer token**.

### Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "username": "admin",
  "role": "admin"
}
```

Use the token in all subsequent requests:
```bash
-H "Authorization: Bearer <your_token_here>"
```

---

## 📋 API Reference

### Airlines

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/airlines` | Create airline |
| `GET` | `/airlines` | List all airlines |
| `GET` | `/airlines/{id}` | Get airline by ID |
| `PUT` | `/airlines/{id}` | Update airline |
| `DELETE` | `/airlines/{id}` | Delete airline |

**Create Airline Request:**
```json
{
  "airline_code": "GA",
  "airline_name": "Garuda Indonesia",
  "contact_person": "John Doe",
  "email": "ops@garuda.com",
  "phone": "+62-21-2351-9999",
  "address": "Soekarno-Hatta Airport, Tangerang"
}
```

---

### Fuel Vendors

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/vendors` | Create vendor |
| `GET` | `/vendors` | List all vendors |
| `GET` | `/vendors/{id}` | Get vendor by ID |
| `PUT` | `/vendors/{id}` | Update vendor |
| `DELETE` | `/vendors/{id}` | Delete vendor |

**Create Vendor Request:**
```json
{
  "vendor_code": "PT-FUEL",
  "vendor_name": "PT Pertamina Fuel",
  "contact_person": "Jane Smith",
  "email": "contact@pertamina.com",
  "phone": "+62-21-1234-5678",
  "address": "Jakarta Pusat, DKI Jakarta"
}
```

---

### Fuel Prices

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/fuel-prices` | Add new price for vendor |
| `PUT` | `/fuel-prices/{id}` | Update a price record |
| `GET` | `/fuel-prices/latest/{vendor_id}` | Get latest price (auto-selected for transactions) |
| `GET` | `/fuel-prices/history/{vendor_id}` | Get full price history |

**Create Price Request:**
```json
{
  "vendor_id": 1,
  "price_per_liter": 12500.0000,
  "effective_date": "2024-06-22"
}
```

---

### Fuel Transactions

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/transactions` | Create transaction (auto-selects latest price) |
| `GET` | `/transactions/{invoice_no}` | Get full invoice by invoice number |

**Create Transaction Request:**
```json
{
  "airline_id": 1,
  "vendor_id": 1,
  "fuel_quantity": 5000.0000,
  "transaction_date": "2024-06-22",
  "remarks": "Regular refuelling – Flight GA-415"
}
```

**Response:**
```json
{
  "id": 1,
  "invoice_no": "INV-20240622-0001",
  "airline_id": 1,
  "vendor_id": 1,
  "fuel_quantity": 5000.0000,
  "fuel_price": 12500.0000,
  "total_amount": 62500000.0000,
  "transaction_date": "2024-06-22",
  "remarks": "Regular refuelling – Flight GA-415"
}
```

---

### Reports

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/reports/invoices` | Invoice report with filters |
| `GET` | `/reports/dashboard` | Dashboard KPIs |

**Report Filters (query params):**

| Param | Type | Example |
|-------|------|---------|
| `from_date` | date | `2024-01-01` |
| `to_date` | date | `2024-12-31` |
| `airline_id` | int | `1` |
| `vendor_id` | int | `1` |

**Dashboard Response:**
```json
{
  "period_from": "2024-01-01",
  "period_to": "2024-12-31",
  "total_transactions": 50,
  "total_fuel_quantity": 250000.0000,
  "total_revenue": 3125000000.0000,
  "top_airlines": [
    {
      "airline_id": 1,
      "airline_name": "Garuda Indonesia",
      "total_fuel": 100000.0000,
      "total_amount": 1250000000.0000
    }
  ],
  "top_vendors": [
    {
      "vendor_id": 1,
      "vendor_name": "PT Pertamina Fuel",
      "total_fuel": 200000.0000,
      "total_amount": 2500000000.0000
    }
  ]
}
```

---

## 🔒 Business Rules

| Rule | Description |
|------|-------------|
| **Rule 1** | A vendor can have multiple fuel price records (full history maintained) |
| **Rule 2** | The **latest** fuel price (`effective_date DESC`) is automatically selected when creating a transaction |
| **Rule 3** | Invoice numbers follow format `INV-YYYYMMDD-XXXX` (e.g. `INV-20240622-0001`) |
| **Rule 4** | `total_amount = fuel_quantity × fuel_price` (calculated server-side) |
| **Rule 5** | If no fuel price exists for the selected vendor, transaction creation returns **HTTP 422** |

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

Tests use an **in-memory SQLite** database and cover:
- ✅ Health check
- ✅ Login success & failure
- ✅ Airline CRUD
- ✅ Vendor CRUD
- ✅ Business Rule #5 (transaction blocked without price → 422)
- ✅ Full happy-path: set price → create transaction → fetch invoice

---

## 🗄️ Database Schema

```
users
├── id (PK)
├── username (UNIQUE)
├── password_hash
└── role (admin | operator | viewer)

airlines
├── id (PK)
├── airline_code (UNIQUE)
├── airline_name
├── contact_person
├── email
├── phone
└── address

fuel_vendors
├── id (PK)
├── vendor_code (UNIQUE)
├── vendor_name
├── contact_person
├── email
├── phone
└── address

fuel_prices
├── id (PK)
├── vendor_id (FK → fuel_vendors.id)
├── price_per_liter
└── effective_date

fuel_transactions
├── id (PK)
├── invoice_no (UNIQUE)
├── airline_id (FK → airlines.id)
├── vendor_id (FK → fuel_vendors.id)
├── fuel_quantity
├── fuel_price          ← snapshot at transaction time
├── total_amount
├── transaction_date
└── remarks
```

---

## 🛠️ Alembic Cheat Sheet

```bash
# Create new migration
alembic revision --autogenerate -m "describe_your_change"

# Apply all pending migrations
alembic upgrade head

# Roll back one step
alembic downgrade -1

# View current revision
alembic current

# View migration history
alembic history --verbose
```

---

## 🏗️ Architecture Overview

```
HTTP Request
    │
    ▼
Controller (FastAPI Router)
    │  validates via DTO (Pydantic)
    ▼
Use Case (Business Logic)
    │  enforces business rules
    ▼
Repository (Data Access)
    │  talks to SQLAlchemy ORM
    ▼
PostgreSQL Database
```

**Layers:**
- **Controllers** — HTTP only, no business logic
- **DTOs** — Input validation & output serialization
- **Use Cases** — Pure business rules, orchestrate repositories
- **Repositories** — All DB queries, no business logic
- **Entities** — Domain objects decoupled from ORM
- **Providers** — Shared infrastructure (DB, JWT, Invoice)

---

## 🔧 Production Checklist

- [ ] Change `SECRET_KEY` to a strong random string (`openssl rand -hex 32`)
- [ ] Set `DEBUG=False` in `.env`
- [ ] Tighten CORS `allow_origins` in `app.py`
- [ ] Change default user passwords after seeding
- [ ] Use a connection pool manager (PgBouncer) for high traffic
- [ ] Set up SSL/TLS on the database connection
- [ ] Configure a reverse proxy (Nginx) in front of Uvicorn
- [ ] Add rate limiting middleware
- [ ] Set up structured logging (e.g. JSON logs for ELK/Datadog)

---

## 📄 License

MIT © Airline Fuel Management System Team
