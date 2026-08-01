<p align="center">
  <img src="docs/images/route_ai_banner.png" alt="AI Route Optimization Platform Banner" width="100%" style="border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.5);">
</p>

<h1 align="center">🚚 AI Route Optimization — Enterprise Logistics & Fleet Intelligence Platform</h1>

<p align="center">
  <b>Autonomous Fleet Dispatching • Dynamic VRP Solver • Predictive ETAs • Multi-Agent Logistics • RAG Intelligence</b>
</p>

<p align="center">
  <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"></a>
  <a href="https://react.dev/"><img src="https://img.shields.io/badge/React-18.2-61DAFB.svg?style=for-the-badge&logo=react&logoColor=black" alt="React 18"></a>
  <a href="https://supabase.com/"><img src="https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E.svg?style=for-the-badge&logo=supabase&logoColor=white" alt="Supabase PostgreSQL"></a>
  <a href="https://tailwindcss.com/"><img src="https://img.shields.io/badge/Tailwind_CSS-3.4-06B6D4.svg?style=for-the-badge&logo=tailwindcss&logoColor=white" alt="Tailwind CSS"></a>
  <a href="https://vercel.com/"><img src="https://img.shields.io/badge/Vercel-Frontend-000000.svg?style=for-the-badge&logo=vercel&logoColor=white" alt="Vercel Deployment"></a>
  <a href="https://render.com/"><img src="https://img.shields.io/badge/Render-Backend-46E3B7.svg?style=for-the-badge&logo=render&logoColor=black" alt="Render Deployment"></a>
</p>

---

## 📋 Table of Contents
- [Overview](#-overview)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Core Modules](#-core-modules)
- [Quick Start Guide](#-quick-start-guide)
  - [Backend Setup (FastAPI)](#1-backend-setup-fastapi)
  - [Frontend Setup (React + Vite)](#2-frontend-setup-react--vite)
  - [Environment Configuration](#3-environment-configuration)
- [Deployment Guide](#-deployment-guide)
- [API Documentation & Swagger UI](#-api-documentation--swagger-ui)
- [Automated Testing](#-automated-testing)
- [Directory Structure](#-directory-structure)
- [License & Contributing](#-license--contributing)

---

## 📦 Overview

Modern enterprise logistics operations face constant unpredictable challenges: severe traffic delays, sudden weather anomalies, emergency order injections, vehicle breakdowns, and strict delivery time windows. Standard static routing systems fail under such dynamic conditions.

**AI Route Optimization** is a state-of-the-art enterprise logistics management platform built to transform fleet operations. By combining mathematical constraint solver algorithms with **AI-powered intelligence**, the platform delivers autonomous route optimization, real-time incident rerouting, machine-learning powered ETA predictions, and natural language dispatch intelligence.

---

## ✨ Key Features

- 🗺️ **Dynamic Vehicle Routing Solver (VRPTW)**: Solves complex multi-depot, multi-vehicle routing problems while strictly respecting vehicle capacity constraints, time windows, and driver break schedules.
- ⚡ **Real-Time Mid-Route Incident Rerouting**: Automatically detects traffic congestion or breakdown events and re-optimizes active driver routes on the fly.
- ⏱️ **ML-Driven Predictive ETAs**: Generates accurate arrival estimations by analyzing historical delivery metrics, road speed profiles, and ambient weather telemetry.
- 💬 **Logistics RAG Assistant**: Conversational assistant for dispatchers and fleet managers to query operating policies, driver compliance records, and active delivery statuses in natural language.
- 📊 **Interactive Operations Mission Control**: High-visibility dashboard built with React 18 and Tailwind CSS for real-time fleet tracking, order assignment, pagination, filtering, search, and logistics KPIs.
- 🛡️ **Enterprise Security & Validation**: JWT Bearer token authentication, Passlib/Bcrypt password hashing, Role-Based Access Control (RBAC), Pydantic v2 cross-field validation, duplicate order detection, and sanitized database error handling.

---

## 🏗️ System Architecture

```
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                               AI ROUTE OPTIMIZATION ARCHITECTURE                                  │
└───────────────────────────────────────────────────────────────────────────────────────────────────┘

 1. REACT 18 FRONTEND (Vite + Tailwind CSS)
    ├── App.jsx ➔ AuthProvider (Context API) ➔ AppRoutes
    ├── MainLayout (Responsive Sidebar + Glassmorphic Navbar)
    ├── DashboardPage & DeliveriesPage Data Grid
    │     ├── Search Input, Status/Priority Filters, Sort Select, Pagination Bar
    │     └── Modals: DeliveryDetailModal, DeliveryFormModal, DeleteConfirmModal
    └── Axios Client Service (`src/api/client.js` & `src/services/deliveryService.js`)
          ├── Request Interceptor: Injects `Authorization: Bearer <JWT>`
          └── Response Interceptor: Catches 401 Unauthorized ➔ Clears Session ➔ Redirects to `/login`
                                                  │
                                                  │ HTTP REST API (JSON)
                                                  ▼
 2. FASTAPI BACKEND API LAYER (backend/app/api/v1/endpoints)
    ├── APIRouter (`/api/v1`)
    ├── OpenAPI 3.0 OpenAPI Spec & Swagger Authorization Scheme
    ├── Dependency Injection:
    │     ├── `Depends(get_db)` ➔ SessionLocal SQLAlchemy Session
    │     ├── `Depends(get_current_user)` ➔ JWT Token Decoding & User Retrieval
    │     └── `Depends(require_role("Admin"))` ➔ RBAC Role Enforcement
    └── Endpoints: Auth, Deliveries, Drivers, Vehicles, Routes, Notifications
                                                  │
                                                  ▼
 3. BUSINESS SERVICE LAYER (backend/app/services)
    ├── Business Rules & Validation
    ├── Duplicate Order Detection (Raises HTTP 409 Conflict if active duplicate exists)
    ├── FSM State Transition Engine (Pending ➔ Scheduled ➔ Assigned ➔ In Transit ➔ Delivered)
    └── Custom Domain Exception Handling (`EntityNotFoundException`, `IllegalStateTransitionException`)
                                                  │
                                                  ▼
 4. REPOSITORY DATA ACCESS LAYER (backend/app/repositories)
    ├── Pure Database Access Abstraction (SQLAlchemy 2.0 `select()` AST queries)
    ├── `list_deliveries()`: Case-insensitive ILIKE search, filter, count optimization, dynamic order_by, offset/limit
    ├── `find_duplicate_delivery()`: Active duplicate query
    └── `create_delivery()`, `update_delivery()`, `delete_delivery()`
                                                  │
                                                  ▼
 5. DATABASE LAYER (Supabase / PostgreSQL)
    ├── SQLAlchemy ORM Models & Supabase PostgreSQL Database
    ├── Composite Index `ix_deliveries_status_created_at` on `(delivery_status, created_at)`
    └── Database Execution via `psycopg2` driver over TCP/IP (Port 5432)
```

---

## 🛠️ Tech Stack

| Layer | Technology | Description |
| :--- | :--- | :--- |
| **Frontend Framework** | React 18 | Vite bundler, React Router 6, React Context API |
| **Styling & UI** | Tailwind CSS 3.4 | Modern glassmorphism, responsive grid/flex layouts, Lucide icons |
| **HTTP Client** | Axios | Request token interceptors & automatic 401 response handling |
| **Backend Framework** | FastAPI 0.110+ | Asynchronous Python framework with automatic Swagger docs |
| **Database & ORM** | Supabase / PostgreSQL | SQLAlchemy 2.0 ORM, Alembic schema migrations |
| **Validation** | Pydantic v2 | High-performance Rust-backed data validation and cross-field rules |
| **Security & Auth** | JWT & Bcrypt | `passlib` password hashing, `python-jose` signed access tokens, RBAC |
| **Deployment** | Vercel & Render | Vercel (Frontend SPA), Render (FastAPI Backend Service) |

---

## 🧩 Core Modules

1. 🔐 **Authentication & Security** (`backend/app/api/v1/endpoints/auth.py`): Handles user registration, JWT login authentication, token verification, and role-based permissions (`Admin`, `User`).
2. 📦 **Delivery Management** (`backend/app/api/v1/endpoints/deliveries.py`): Captures package orders, enforces weight/dimension limits, calculates time windows, and runs status state machines.
3. 🚚 **Driver Management** (`backend/app/repositories/driver.py`): Manages commercial driver profiles, shift schedules, hours-of-service compliance, and license validation.
4. 🚛 **Vehicle Fleet Management** (`backend/app/repositories/vehicle.py`): Tracks vehicle capacities, fuel/battery telemetry, maintenance schedules, and EV battery ranges.
5. 🗺️ **VRP Route Optimizer** (`backend/app/repositories/route.py`): Solves multi-vehicle routing problems using mathematical heuristics to minimize total mileage and emissions.
6. 🔔 **Notification Engine** (`backend/app/repositories/notification.py`): Handles system telemetry alerts, driver dispatch notifications, and order updates.

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python**: `v3.11` or higher
- **Node.js**: `v18.0` or higher (`npm v9+`)
- **PostgreSQL / Supabase**: Connection URI string

---

### 1. Backend Setup (FastAPI)

```powershell
# 1. Navigate to backend directory
cd backend

# 2. Create and activate Python virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # On Windows
source .venv/bin/activate      # On Linux/macOS

# 3. Install backend dependencies
pip install -r requirements.txt

# 4. Configure environment variables (.env)
cp .env.example .env

# 5. Run Database Migrations (Alembic)
python -m alembic upgrade head

# 6. Start Uvicorn ASGI Server
python -m uvicorn app.main:app --reload --port 8000
```

The FastAPI backend will start at: **`http://localhost:8000`**

---

### 2. Frontend Setup (React + Vite)

```powershell
# 1. Open a second terminal and navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start Vite development server
npm run dev
```

The React frontend dashboard will open at: **`http://localhost:3000`**

---

### 3. Environment Configuration

Create a `.env` file inside `backend/`:

```env
PROJECT_NAME="AI Route Optimization"
API_V1_STR="/api/v1"
DATABASE_URL="postgresql+psycopg2://postgres:[YOUR-PASSWORD]@db.[YOUR-SUPABASE-ID].supabase.co:5432/postgres"
SECRET_KEY="your-super-secret-jwt-key-here"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=11520
CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
```

---

## ☁️ Deployment Guide

### Deploy Frontend to Vercel
The repository includes a root `vercel.json` configuration:
```bash
npm install -g vercel
vercel --prod
```

### Deploy Backend to Render
The repository includes a root `render.yaml` configuration defining the FastAPI web service:
- **Build Command**: `pip install -r backend/requirements.txt`
- **Start Command**: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`

---

## 📑 API Documentation & Swagger UI

FastAPI automatically generates interactive OpenAPI 3.0 documentation:

- 📖 **Interactive Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- 📚 **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- 📄 **Raw OpenAPI Spec (JSON)**: [http://localhost:8000/api/v1/openapi.json](http://localhost:8000/api/v1/openapi.json)

---

## 🧪 Automated Testing

The backend includes a comprehensive automated Pytest test suite covering authentication, RBAC authorization, CRUD operations, pagination, search, filtering, duplicate order detection, and FSM transition enforcement.

Run the test suite:

```powershell
cd backend
python -m pytest tests/ -v
```

```
======================== 20 passed, 3 warnings in 5.13s ========================
```

---

## 📁 Directory Structure

```
AI Route Optimization/
├── docs/                      # Documentation assets & architecture diagrams
│   └── images/                # Banner and screenshot assets
│       └── route_ai_banner.png
├── backend/                   # FastAPI Backend Application
│   ├── alembic/               # Alembic database migration scripts
│   ├── app/
│   │   ├── api/               # API endpoints (auth, deliveries, drivers, routes, etc.)
│   │   ├── core/              # Config settings, security, exception handlers
│   │   ├── db/                # Database session & base declarative models
│   │   ├── models/            # SQLAlchemy ORM Database models
│   │   ├── repositories/      # Data access layer (SQL queries & pagination)
│   │   ├── schemas/           # Pydantic request validation & response DTOs
│   │   ├── services/          # Core business logic & state machine rules
│   │   └── main.py            # FastAPI application entry point
│   ├── tests/                 # Pytest automated test suite
│   └── requirements.txt
├── frontend/                  # React + Vite Dashboard Application
│   ├── src/
│   │   ├── api/               # Axios client instance with request/response interceptors
│   │   ├── components/        # UI components & interactive action modals
│   │   ├── context/           # React Context API global auth state
│   │   ├── layouts/           # Main responsive sidebar & navbar layouts
│   │   ├── pages/             # Dashboard and Delivery data grid pages
│   │   └── services/          # API service integration layer
│   └── package.json
├── render.yaml                # Render backend deployment config
├── vercel.json                # Vercel frontend deployment config
└── README.md                  # Master GitHub repository README
```

---

## 📄 License & Contributing

Distributed under the **MIT License**. Contributions, issues, and feature requests are welcome!

---

<p align="center">
  Developed with ❤️ for Advanced AI Logistics & Fleet Engineering.
</p>
