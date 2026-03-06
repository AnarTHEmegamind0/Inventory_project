# Agent Context: Image-Based Product Recognition & Automated Audit Decision System

> **Bachelor Thesis Project** — A retail inventory audit system that photographs store shelves, detects products with YOLOv8, compares against expected inventory, and returns an automated audit decision (PASS / WARNING / FAIL).

---

## ⚠️ CRITICAL: Read Before Doing Anything

1. **Read this entire file** before making changes.
2. **Read `STEPS.md`** to know the exact implementation sequence.
3. **Consult installed skills** (listed below) for domain-specific best practices.
4. **Never guess** — if unsure, check the source code first.
5. **Follow the STEPS.md order** — each step depends on previous steps being complete.

---

## System Overview

```
┌──────────────┐     HTTP/REST      ┌──────────────┐     YOLO Model     ┌──────────────┐
│   Frontend   │ ──────────────────▶ │   Backend    │ ──────────────────▶ │  ML Pipeline │
│  (React.js)  │ ◀────── JSON ────── │  (FastAPI)   │ ◀── Detections ──── │  (YOLOv8)    │
│  Port: 3000  │                     │  Port: 8000  │                     │  PyTorch     │
└──────────────┘                     └──────┬───────┘                     └──────────────┘
                                            │
                                     ┌──────▼───────┐
                                     │   MongoDB     │
                                     │  Port: 27017  │
                                     │  DB: inventory│
                                     │      _audit   │
                                     └──────────────┘
```

---

## Tech Stack & Exact Versions

| Layer               | Technology              | Version    |
|---------------------|-------------------------|------------|
| **ML Framework**    | YOLOv8 (Ultralytics)    | 8.3.241    |
| **Deep Learning**   | PyTorch                 | 2.9.1      |
| **Computer Vision** | OpenCV                  | 4.12.0     |
| **Backend API**     | FastAPI                 | 0.115.0    |
| **Database Driver** | Motor (async MongoDB)   | 3.6.0      |
| **Validation**      | Pydantic                | 2.9.0      |
| **Frontend**        | React.js                | 18.3.0     |
| **Frontend Router** | react-router-dom        | 6.26.0     |
| **HTTP Client**     | Axios                   | 1.7.0      |
| **Charts**          | Recharts                | 2.12.0     |
| **Containerization**| Docker Compose          | 3.8        |
| **Testing**         | Pytest                  | 8.3.0      |

---

## 📁 Complete File Map

### 1. Backend — `backend/app/` (FastAPI REST API)

```
backend/
├── Dockerfile
├── requirements.txt
└── app/
    ├── __init__.py
    ├── main.py                      # FastAPI app, CORS, lifespan, router mounting
    ├── config.py                    # Settings dataclass — loads ALL env vars
    ├── database.py                  # Motor async MongoDB — connect/disconnect/collections
    ├── models/
    │   ├── detection.py             # DetectionResult, DetectionItem Pydantic schemas
    │   ├── audit.py                 # AuditResult, AuditStatus Pydantic schemas
    │   └── product.py               # Product CRUD Pydantic schemas
    ├── routes/
    │   ├── detection.py             # POST /api/detection/detect — image upload
    │   ├── audit.py                 # POST /api/audit/run, GET /history, /stats
    │   └── products.py              # CRUD /api/products + inventory summary
    └── services/
        ├── detection_service.py     # Singleton ProductDetector, calls src/inference/
        └── audit_service.py         # Singleton AuditEngine, calls src/inference/
```

**⚡ Current State:**
- `routes/detection.py` line 44-57: Detection is **PLACEHOLDER** — returns empty results with "Model not loaded yet" message. The `ProductDetector` import is commented out.
- `routes/audit.py`: Working — imports `AuditEngine` directly (should use `AuditService` instead).
- `routes/products.py`: Working — full CRUD + inventory summary aggregation.
- `services/detection_service.py`: Working — singleton pattern, checks `MODEL_PATH` exists.
- `services/audit_service.py`: Working — singleton pattern with configurable thresholds.

**Ownership Rules:**
- `routes/` → HTTP only (parse request, return response). NO business logic.
- `services/` → ALL business logic. Call `src/inference/` for ML.
- `models/` → Pydantic schemas only. Shared across routes and services.

---

### 2. ML Pipeline — `src/` (Core Thesis Code)

```
src/
├── __init__.py
├── data/
│   ├── augment.py               # random_brightness, random_flip, random_rotation, add_noise, random_blur, augment_dataset()
│   ├── preprocess.py            # resize_image(), normalize_image()
│   └── split_dataset.py         # split_dataset() → train/val/test (70/20/10 default)
├── training/
│   ├── train.py                 # train_model() + validate_model() — ultralytics YOLO API
│   ├── evaluate.py              # mAP, precision, recall evaluation
│   └── hyperparams.py           # Hyperparameter configuration
├── inference/
│   ├── detector.py              # Detection, DetectionResult, ProductDetector class
│   └── audit_engine.py          # AuditStatus, ProductDiscrepancy, AuditResult, AuditEngine class
└── utils/
    ├── logger.py                # Structured logging
    └── visualization.py         # Draw bounding boxes on images
```

**⚡ Current State:**
- `detector.py`: Fully implemented. `ProductDetector` loads YOLO, runs inference, returns `DetectionResult`. Has `detect()`, `detect_batch()`, `draw_detections()`. **BUG on line 172**: `cv2.getFontSize = cv2.getTextSize(...)` — assignment to wrong variable name.
- `audit_engine.py`: Fully implemented. `AuditEngine` with `run_audit()` and `generate_report()`. Tolerance/threshold logic correct.
- `augment.py`: **BUG on line 1**: `cla"""` should be `"""` (typo prefix).
- `split_dataset.py`: Fully implemented. Default seed=42 for reproducibility.
- `train.py`: Fully implemented. Uses `yolov8n.pt` base model, 100 epochs default.

**Ownership Rules:**
- `ProductDetector` = **SINGLE ENTRY POINT** for all YOLO inference.
- `AuditEngine` = **SINGLE ENTRY POINT** for all audit decisions.
- `src/training/` and `src/data/` = Standalone offline scripts, NOT called at runtime.

---

### 3. Frontend — `frontend/src/` (React.js Dashboard)

```
frontend/
├── Dockerfile
├── package.json                  # React 18.3, react-scripts (CRA), axios, recharts
└── src/
    ├── App.js                    # Root component, routing
    ├── App.css                   # Global styles
    ├── index.js                  # React entry point
    ├── services/
    │   └── api.js                # Axios client — ALL backend calls go through here
    ├── pages/
    │   ├── Dashboard.js          # Stats overview (uses recharts)
    │   ├── Upload.js             # Image upload → POST /api/detection/detect
    │   ├── Products.js           # CRUD UI for expected inventory
    │   └── AuditReport.js        # Audit report with pass/warn/fail breakdown
    └── components/               # (empty — reusable components go here)
```

**⚡ Current State:**
- Uses **Create React App** (react-scripts 5.0.1). Consider migrating to **Vite**.
- `api.js`: Fully implemented — `detectProducts`, `getDetectionHistory`, `runAudit`, `getAuditHistory`, `getAuditStats`, `getProducts`, `createProduct`, `deleteProduct`.
- `REACT_APP_API_URL` env var points to `http://localhost:8000/api`.

**Ownership Rules:**
- `services/api.js` → **SINGLE SOURCE** for all HTTP calls. Never use fetch/axios directly in components.
- `pages/` → One component per route.
- `components/` → Shared reusable UI pieces.

---

### 4. Tests — `tests/`

```
tests/
├── __init__.py
├── test_api.py                  # ⚠️ Uses raw `requests` to running server (not TestClient)
├── test_detector.py             # Tests preprocess functions + DetectionResult.to_dict()
└── test_audit_engine.py         # Tests all audit scenarios (pass/warn/fail/extra/missing)
```

**⚡ Current State:**
- `test_api.py`: Tests require running server. Should be refactored to use `FastAPI TestClient`.
- `test_detector.py`: Tests preprocessing + serialization. Does NOT test actual YOLO inference.
- `test_audit_engine.py`: Comprehensive — 6 tests covering all audit scenarios. **This is the best test file.**

---

### 5. Data & Models

```
data/
├── raw/                          # Original unprocessed images (EMPTY)
├── labeled/                      # Images + YOLO format .txt labels (EMPTY)
├── augmented/                    # Augmented training data (EMPTY)
└── splits/                       # Train/val/test splits (EMPTY)

models/
├── configs/
│   └── dataset.yaml             # ⚠️ PLACEHOLDER classes (product_a, product_b, product_c)
├── weights/                      # YOLO .pt files (EMPTY — no trained model yet)
└── exports/                      # Exported models (EMPTY)
```

---

### 6. Infrastructure

```
docker-compose.yml               # 3 services: mongodb (:27017), backend (:8000), frontend (:3000)
.env.example                     # All 11 environment variables with defaults
requirements.txt                 # All Python dependencies with pinned versions
.gitignore                       # Standard ignores
```

---

## 🔌 Installed Skills Reference

Skills provide domain-specific best practices. **Read the relevant SKILL.md before working on that domain.**

### Location: `.agents/skills/` AND `.claude/skills/` (symlinked, same content)

| Skill | Location | When to Consult |
|-------|----------|-----------------|
| **senior-computer-vision** | `.agents/skills/senior-computer-vision/SKILL.md` | Working on `src/inference/detector.py`, image preprocessing, model architecture decisions |
| **computer-vision-opencv** | `.agents/skills/computer-vision-opencv/SKILL.md` | Working with OpenCV operations in `src/data/`, `src/utils/visualization.py` |
| **opencv** | `.agents/skills/opencv/SKILL.md` | Any OpenCV-related image processing |
| **yolo** | `.agents/skills/yolo/SKILL.md` | Training, inference, detection logic, YOLO-specific patterns |
| **machine-learning-engineer** | `.agents/skills/machine-learning-engineer/SKILL.md` | ML architecture decisions, training strategy, evaluation |
| **ml-model-training** | `.agents/skills/ml-model-training/SKILL.md` | `src/training/train.py`, hyperparameter tuning, data splits |
| **fastapi-expert** | `.agents/skills/fastapi-expert/SKILL.md` | Working on `backend/app/` — routes, services, middleware, async patterns |
| **mongodb** | `.agents/skills/mongodb/SKILL.md` | Working on `backend/app/database.py`, MongoDB queries, aggregations |
| **react-vite-expert** | `.agents/skills/react-vite-expert/SKILL.md` | Working on `frontend/` — React components, Vite migration, state management |
| **python-testing** | `.agents/skills/python-testing/SKILL.md` | Writing tests in `tests/`, pytest patterns, mocking |
| **docker-patterns** | `.agents/skills/docker-patterns/SKILL.md` | Working on `docker-compose.yml`, Dockerfiles, containerization |
| **find-skills** | `.agents/skills/find-skills/SKILL.md` | Searching for new skills with `npx skills find` |

### Skill Reference Files (Deep Knowledge)

```
senior-computer-vision/references/
├── object_detection_optimization.md   # Optimization techniques for detection models
├── computer_vision_architectures.md   # Architecture patterns and best practices
└── production_vision_systems.md       # Production deployment patterns

yolo/references/
├── detection-logic.md                 # YOLO detection logic details
├── testing-procedures.md              # YOLO testing best practices
├── automation-workflows.md            # CI/CD for YOLO projects
├── post-push-automation.md            # Post-deployment automation
└── secrets-extraction.md              # Config/secrets management
```

### How to Use Skills

1. **Before working on a domain**, read the relevant `SKILL.md` file.
2. **Follow the patterns** described in the skill — they contain field-tested best practices.
3. **Check reference files** for deep knowledge when making architecture decisions.
4. **If a needed skill doesn't exist**, search: `npx skills find "your query"`.

---

## Core Data Flow (10-Step Pipeline)

```
 1. User uploads shelf image (React Upload.js)
        │
        ▼
 2. POST /api/detection/detect (multipart/form-data)
        │
        ▼
 3. detection route saves image → data/uploads/
        │
        ▼
 4. DetectionService calls ProductDetector.detect(image)
        │   ├─ Loads YOLOv8 from MODEL_PATH
        │   ├─ Runs inference (CONFIDENCE_THRESHOLD=0.25, IOU_THRESHOLD=0.45)
        │   └─ Returns: DetectionResult { detections[], total_products, processing_time_ms }
        │
        ▼
 5. Saves to MongoDB → detections collection
        │
        ▼
 6. Returns JSON to frontend → displayed in Results
        │
        ▼
 7. POST /api/audit/run (with expected_inventory + detected_products)
        │
        ▼
 8. AuditService calls AuditEngine.run_audit(expected, detected)
        │   ├─ Per product: diff ≤ 10% → PASS, 10-30% → WARNING, > 30% → FAIL
        │   ├─ Expected but missing → FAIL
        │   └─ Unexpected extra → WARNING
        │
        ▼
 9. Saves to MongoDB → audits collection
        │
        ▼
10. Returns AuditResult JSON → displayed in AuditReport.js
```

---

## API Endpoints

| Method | Endpoint                     | Description                        | Request Body           |
|--------|------------------------------|------------------------------------|------------------------|
| GET    | `/`                          | API info                           | —                      |
| GET    | `/health`                    | Health check                       | —                      |
| POST   | `/api/detection/detect`      | Upload image → detect products     | `multipart/form-data`  |
| GET    | `/api/detection/history`     | List past detections               | `?limit=20&skip=0`     |
| GET    | `/api/detection/{id}`        | Get single detection               | —                      |
| POST   | `/api/audit/run`             | Run audit comparison               | `AuditRequest` JSON    |
| GET    | `/api/audit/history`         | List past audits                   | `?limit=20&skip=0`     |
| GET    | `/api/audit/stats`           | Aggregate statistics               | —                      |
| GET    | `/api/audit/{id}`            | Get single audit                   | —                      |
| GET    | `/api/products/`             | List products                      | `?category=&location=` |
| POST   | `/api/products/`             | Create product                     | `ProductCreate` JSON   |
| GET    | `/api/products/{name}`       | Get product by name                | —                      |
| PUT    | `/api/products/{name}`       | Update product                     | `ProductUpdate` JSON   |
| DELETE | `/api/products/{name}`       | Delete product                     | —                      |
| GET    | `/api/products/inventory/summary` | Category summary              | —                      |

---

## Environment Variables (`.env`)

| Variable                   | Default                          | Used By   |
|----------------------------|----------------------------------|-----------|
| `MONGODB_URI`              | `mongodb://localhost:27017`      | Backend   |
| `MONGODB_DB_NAME`          | `inventory_audit`                | Backend   |
| `API_HOST`                 | `0.0.0.0`                        | Backend   |
| `API_PORT`                 | `8000`                           | Backend   |
| `API_DEBUG`                | `true`                           | Backend   |
| `MODEL_PATH`               | `models/weights/.../best.pt`     | ML        |
| `CONFIDENCE_THRESHOLD`     | `0.25`                           | ML        |
| `IOU_THRESHOLD`            | `0.45`                           | ML        |
| `AUDIT_TOLERANCE`          | `0.1` (10%)                      | Audit     |
| `AUDIT_CRITICAL_THRESHOLD` | `0.3` (30%)                      | Audit     |
| `UPLOAD_DIR`               | `data/uploads`                   | Backend   |
| `MAX_UPLOAD_SIZE`          | `10485760` (10MB)                | Backend   |
| `CORS_ORIGINS`             | `localhost:3000,localhost:5173`   | Backend   |
| `REACT_APP_API_URL`        | `http://localhost:8000/api`      | Frontend  |

---

## MongoDB Collections

| Collection     | Key Fields                                                | Written By          |
|----------------|-----------------------------------------------------------|---------------------|
| `detections`   | `image_path`, `detections[]`, `timestamp`, `total_products`, `processing_time_ms` | `detection` route |
| `audits`       | `audit_id`, `status`, `match_rate`, `discrepancies[]`, `missing_products[]`, `extra_products[]` | `audit` route |
| `products`     | `name`, `category`, `expected_count`, `location`, `sku`, `created_at`, `updated_at` | `products` route |

---

## Known Bugs & TODOs

| File | Line | Issue |
|------|------|-------|
| `src/data/augment.py` | 1 | `cla"""` should be `"""` — typo prefix |
| `src/inference/detector.py` | 172 | `cv2.getFontSize = cv2.getTextSize(...)` — wrong variable assignment |
| `backend/app/routes/detection.py` | 44-57 | Detection is PLACEHOLDER — `ProductDetector` commented out |
| `backend/app/routes/audit.py` | 34 | Imports `AuditEngine` directly instead of using `AuditService` |
| `tests/test_api.py` | all | Uses raw `requests` to running server, should use `TestClient` |
| `models/configs/dataset.yaml` | 14-17 | PLACEHOLDER classes (`product_a/b/c`), needs real product names |
| `data/` | all | ALL data directories are EMPTY — no training data yet |
| `models/weights/` | — | NO trained model exists yet |

---

## Commands

```bash
# ── Backend ──
source inventory_env/bin/activate
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

# ── Frontend ──
cd frontend && npm start           # Dev server on :3000

# ── Docker (Full Stack) ──
docker-compose up --build          # MongoDB + Backend + Frontend

# ── ML Training ──
python -m src.training.train       # Train YOLOv8 model
python -m src.training.evaluate    # Evaluate model metrics

# ── Data Preparation ──
python -m src.data.split_dataset   # Split into train/val/test
python -m src.data.augment         # Augment training images
python -m src.data.preprocess      # Preprocess images

# ── Tests ──
pytest tests/                      # Run all tests
pytest tests/test_detector.py      # Test ML detector only
pytest tests/test_audit_engine.py  # Test audit logic only
pytest tests/test_api.py           # Test API endpoints only
```

---

## Coding Conventions

| Rule                     | Details                                                    |
|--------------------------|------------------------------------------------------------|
| **API format**           | All responses use `snake_case` keys                        |
| **Async**                | Backend uses `async/await` everywhere (Motor for MongoDB)  |
| **Timestamps**           | ISO 8601 format (`2024-01-15T10:30:00`)                    |
| **Model weights**        | Stored in `models/weights/`, gitignored                    |
| **Uploads**              | Stored in `data/uploads/`, gitignored                      |
| **Config**               | All tunables via `.env` → loaded by `backend/app/config.py`|
| **Validation**           | Pydantic models for all request/response schemas           |
| **Error handling**       | FastAPI HTTPException with meaningful status codes          |
| **Frontend API calls**   | Always through `services/api.js`, never direct fetch       |
| **Singletons**           | `DetectionService` and `AuditService` use class-level singletons |

---

## Agent Collaboration Rules

1. **Read this file + STEPS.md** before making any changes.
2. **Consult the relevant skill** before working on any domain (see skills table above).
3. **Respect ownership** — routes = HTTP only, services = business logic, models = schemas only.
4. **Single entry points** — `ProductDetector` for inference, `AuditEngine` for audit, `api.js` for frontend HTTP.
5. **Environment config** — NEVER hardcode values. Use `.env` → `config.py`.
6. **Fix known bugs** — check the Known Bugs table before starting. Fix any bugs you encounter in files you touch.
7. **Test after changes** — run `pytest tests/` after any backend/ML change.
8. **Schema sync** — if you change a Pydantic model, update MongoDB writes AND `api.js`.
9. **Docker sync** — if you add env vars/deps, update `docker-compose.yml`, `.env.example`, `requirements.txt`.
10. **Follow STEPS.md** — do steps in order, mark them complete, never skip ahead.
