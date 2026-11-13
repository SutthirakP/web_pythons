# 🐍 web_pythons — FastAPI Learning Journal

> Homework and class projects from a Python web development course.
> From basic CRUD → databases and relationships → login → GraphQL / WebSocket / Streaming → Lifespan, Testing, Rate limiting, CORS and Cookies.

<br>

## 📑 Table of Contents

1. [Overview](#-overview)
2. [Tech Stack](#-tech-stack)
3. [Backend Systems](#-backend-systems)
4. [Frontend Pages](#-frontend-pages)
5. [Databases (SQL / Redis)](#-databases-sql--redis)
6. [Main Project: Catalog](#-main-project-catalog)
7. [Installation](#-installation)
8. [Running the Project](#-running-the-project)
9. [Required Files](#-required-files)
10. [Folder Structure](#-folder-structure)
11. [Next Steps](#-next-steps)

<br>

---

## 🧭 Overview

The project has **3 parts** that work together.

| Part | What it is | Where |
|---|---|---|
| **Backend** | Several **FastAPI** apps, one per topic, each running on its own port | Top-level folders (`appm2m/`, `graphql_demo/`, …) |
| **Frontend** | **Next.js + React** web pages that call the APIs above | `frontend/` |
| **Databases** | **SQLite** (one `.db` file per app) + **Redis** (via Docker) | Created automatically on first run |

<br>

---

## 🛠 Tech Stack

| Area | Tools |
|---|---|
| Languages | Python 3.12+, TypeScript |
| Backend framework | FastAPI, Uvicorn, Pydantic |
| Databases | SQLite + SQLAlchemy (ORM), aiosqlite, Redis |
| Auth / security | JWT (PyJWT), bcrypt / pwdlib, HttpOnly cookies, CORS |
| Other API styles | GraphQL (Strawberry), WebSocket, Server-Sent Events |
| AI | TensorFlow / Keras (Teachable Machine model), Pillow |
| Templates | Jinja2 |
| Rate limiting | slowapi, Redis `INCR` + `EXPIRE` |
| Frontend | Next.js 16, React 19, Tailwind CSS 4 |
| Testing | pytest + FastAPI `TestClient` |
| Tooling | uv (Python packages), Docker (Redis), npm |

<br>

---

## ⚙️ Backend Systems

Listed in the order they were learned — every folder has its own `README.md` with details.

| # | Folder | System | What it teaches | Port |
|:-:|---|---|---|:-:|
| 1 | [`crud_basics/`](crud_basics/) | Students / Products | GET · POST · PUT · DELETE, Pydantic, in-memory list → SQLite | 8000 · 8001 · 8004 |
| 2 | [`appv/`](appv/) | Students ↔ Phone numbers | **One-to-many** (`ForeignKey` + `relationship`) | 8003 |
| 3 | [`appm2m/`](appm2m/) | **Catalog (main project)** | Many-to-many + every later homework — [see below](#-main-project-catalog) | 8002 |
| 4 | [`jwt/`](jwt/) | First login system | Create/verify JWT, password hashing, logout with a blacklist | 8007 |
| 5 | [`image_process/`](image_process/) | AI image prediction | Load a Keras model and serve it as `/predict` | 8006 |
| 6 | [`sse_demo/`](sse_demo/) | Streaming | `StreamingResponse` word by word, Pydantic Settings + `.env` | 8000 |
| 7 | [`graphql_demo/`](graphql_demo/) | GraphQL shop | Queries / mutations with Strawberry + SQLite | 8005 |
| 8 | [`websocket/`](websocket/) | Product notifications | WebSocket, `ConnectionManager`, broadcast | 8000 |
| 9 | [`upload/`](upload/) | File upload | `UploadFile`, `uuid4` file names, `FileResponse` | 8000 |
| 10 | [`fast-lifespan-demo/`](fast-lifespan-demo/) | Lifespan + tests | Load a model / open a DB once, `TestClient` with `with` | 8000 |
| 11 | [`fastapi-latelimits-demo/`](fastapi-latelimits-demo/) | Rate limit + cache | slowapi, a hand-written Redis limiter, response caching | 8000 |
| 12 | [`reservation-demo/`](reservation-demo/) | Last-item reservation | `asyncio.Lock` against race conditions, 30-second hold | 8000 |
| 13 | [`fastapi-template-engine/`](fastapi-template-engine/) | HTML dashboard | Jinja2: `extends` / `block` / `include`, forms + static files | 8000 |
| 14 | [`fastapi_validation_lesson/`](fastapi_validation_lesson/) | Product validation | `Field`, `field_validator`, `model_validator` | 8000 |
| 15 | [`cookie/`](cookie/) | Remember the user | `set_cookie`, `Cookie()`, `delete_cookie`, session ID | 8000 |

> The demos on port **8000** are separate apps — run **one at a time**.

<br>

---

## 🖥 Frontend Pages

The Next.js app lives in [`frontend/`](frontend/) — open **http://localhost:3000**

| Page | Backend | What you can do |
|---|---|---|
| `/` | `crud_basics/main.py` (8000) | Manage students and scores |
| `/products` | `crud_basics/product_db.py` (8001) | Add / edit / delete products stored in SQLite |
| `/catalog` | `appm2m` (8002) | **Main page** — products + categories + images + login + chatbot + CORS test + ✨ streaming |
| `/graphql-shop` | `graphql_demo` (8005) | A shop that talks to the API through GraphQL |

> ⚠️ Open the site with **`localhost`**, not `127.0.0.1` — the `/catalog` login cookie only works when the page and the API are on the same site.

<br>

---

## 🗄 Databases (SQL / Redis)

`.db` files are **not in the repository** (they may contain user data). Each app creates its file and tables on first run.

### SQLite

| Database file | App | Tables | Relationship |
|---|---|---|---|
| `crud_basics/database.db` | student_db | `students` | — |
| `crud_basics/product.db` | product_db | `products` | — |
| `appv/database.db` | appv | `students`, `phones` | **1 : N** — one student has many phone numbers |
| `appm2m/catalog.db` | Catalog | `products`, `categories`, `product_categories`, `users` | **N : M** — products ↔ categories through a join table |
| `graphql_demo/graphql.db` | GraphQL | `products`, `freed_ids` | `freed_ids` remembers deleted ids for reuse |
| `fast-lifespan-demo/app.db` | Lifespan | `predictions_logs` | — (raw SQL with aiosqlite) |

### Redis

| Used for | Key | Expires after |
|---|---|---|
| Counting login attempts (rate limit) | `rate:login:<ip>` | 60 seconds |
| Cookie login sessions | `session:<random id>` | 1 hour / 7 days ("Remember me") |
| Cache / rate-limit demos | `rate:…`, `cache:slow-data` | 30–60 seconds |

<br>

---

## ⭐ Main Project: Catalog

Every homework from many-to-many onwards was built into one project — [`appm2m/`](appm2m/) + the `/catalog` page.

| Feature | Files | What it does |
|---|---|---|
| Products ↔ categories | `models.py`, `main.py` | Many-to-many CRUD for products and categories |
| Register / login | `auth.py` | bcrypt password hashing, JWT, only logged-in users can add/edit/delete |
| Cookie login | `session.py`, `auth.py` | HttpOnly session cookie, **Remember me** option, `GET /me` |
| Product images | `upload.py` | Checks file type/size, random file names, blocks `../` |
| Chatbot | `chatbot.py` | WebSocket replies word by word, notifies everyone when a product changes |
| ✨ Product description writer | `streaming.py` | Server-Sent Events stream the text word by word |
| CORS | `cors.py` | Allows every method except HEAD, with a test button on the page |
| Rate limit | `rate_limit.py` | 5 login attempts per minute, counted in Redis |
| Lifespan | `main.py` | Creates tables and checks the DB/Redis connection at startup, `GET /health` |
| Tests | `conftest.py`, `test_main.py` | **40 pytest tests** (temporary database, real data untouched) |

Guides (in Thai): [`RATE_LIMIT.md`](appm2m/RATE_LIMIT.md) · [`CORS_STREAMING.md`](appm2m/CORS_STREAMING.md) · [`COOKIE.md`](appm2m/COOKIE.md) · [`TESTING.md`](fast-lifespan-demo/TESTING.md)

<br>

---

## 📦 Installation

### 1. Prerequisites

| Program | Version | Used for | Download |
|---|---|---|---|
| **Python** | 3.12 or newer | Running the backend | https://www.python.org/downloads/ |
| **uv** | latest | Installing Python packages | https://docs.astral.sh/uv/ |
| **Node.js** | 20 or newer | Running the frontend | https://nodejs.org/ |
| **Docker Desktop** | latest | Running Redis | https://www.docker.com/products/docker-desktop/ |
| Git | — | Getting the code | https://git-scm.com/ |

### 2. Clone the repository

```powershell
git clone https://github.com/SutthirakP/web_pythons.git
cd web_pythons
```

### 3. Install the backend (Python)

```powershell
uv sync
```

One command creates `.venv` and installs every package from `pyproject.toml` + `uv.lock` (including `pytest`).

### 4. Install the frontend

```powershell
cd frontend
npm install
cd ..
```

### 5. Create Redis (first time only)

```powershell
docker run -d --name my-radis -p 6379:6379 --restart unless-stopped redis:7
docker exec -it my-radis redis-cli ping      # should print PONG
```

> `--restart unless-stopped` = Redis starts automatically whenever Docker Desktop opens.

### 6. Set up `.env` (only for `sse_demo`)

```powershell
copy sse_demo\.env.example sse_demo\.env
```

Then change `SECRET_KEY` in `.env` — this file must **never be committed**.

<br>

---

## ▶️ Running the Project

### Start all main backends with one command

```powershell
uv run python run_all.py
```

Starts ports **8000 – 8005** together and checks/starts Redis for you (Docker Desktop must be open). Press `Ctrl+C` to stop everything.

### Start the frontend

```powershell
cd frontend
npm run dev
```

Then open **http://localhost:3000/catalog**

### Run one app / run the tests

```powershell
uv run fastapi dev appm2m/main.py --port 8002     # Catalog only
uv run pytest appm2m -v                            # Catalog tests (Redis must be running)
```

- Every backend has an interactive API page at `http://127.0.0.1:<port>/docs`
- All commands, the full port table and troubleshooting tips are in **[RUN.md](RUN.md)** (Thai)

<br>

---

## 📋 Required Files

| File | Purpose | Without it |
|---|---|---|
| `pyproject.toml` | List of Python packages | `uv sync` doesn't know what to install |
| `uv.lock` | Locks exact versions so every machine matches | You may get incompatible versions |
| `run_all.py` | Starts all main backends + Redis | You must start each app by hand |
| `frontend/package.json` + `package-lock.json` | Frontend packages | `npm install` fails |
| `image_process/model/keras_model.h5` + `labels.txt` | The trained AI model | `/predict` doesn't work |
| `sse_demo/.env` | Stores `SECRET_KEY` | Falls back to a default (development only) |
| Redis container `my-radis` | Rate limiting + login sessions | `/catalog` login returns **503** |

**Intentionally not in the repository:** `*.db` files · uploaded images (`uploads/`) · `.env` · `.venv/` · `node_modules/` — they are all recreated during installation or at runtime.

<br>

---

## 🗂 Folder Structure

```
web_pythons/
├── appm2m/                    ⭐ Catalog — main project (many-to-many + all homework)
├── appv/                      one-to-many
├── crud_basics/               basic CRUD (list → SQLite)
├── jwt/                       first JWT login
├── graphql_demo/              GraphQL + SQLite
├── websocket/                 WebSocket notifications
├── sse_demo/                  streaming response
├── upload/                    file upload
├── image_process/             AI image prediction (Keras)
├── fast-lifespan-demo/        lifespan + pytest
├── fastapi-latelimits-demo/   rate limit + Redis cache
├── reservation-demo/          last-item reservation (Lock)
├── fastapi-template-engine/   Jinja2 templates
├── fastapi_validation_lesson/ Pydantic validation
├── cookie/                    cookie sessions
├── frontend/                  Next.js (all web pages)
├── run_all.py                 start main backends + Redis
├── RUN.md                     every run command + ports
├── pyproject.toml / uv.lock   Python dependencies
└── README.md                  this file
```

<br>

---

## 🚀 Next Steps

- [ ] **Redesign the web pages** — pick a UI template first, then give every page (`/`, `/products`, `/catalog`, `/graphql-shop`) the same design
- [ ] Add a shared layout / navbar for all pages
- [ ] Make every page responsive on mobile

<br>

---

<sub>Made by SutthirakP · Python Web Development course</sub>
