# Image-Based Product Recognition and Automated Audit Decision System

A machine learning system that uses YOLO object detection to recognize retail products from images and automatically generate inventory audit decisions. Flutter mobile app sends shelf images to Python backend for processing.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           FLUTTER MOBILE APP                             │
│                                                                          │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────────────────┐    │
│  │ Camera Screen │  │ Results Screen│  │ History Screen            │    │
│  │               │  │               │  │                           │    │
│  │ - Take photo  │  │ - Detection   │  │ - Past audits             │    │
│  │ - Gallery     │  │   results     │  │ - Statistics              │    │
│  │   picker      │  │ - Audit       │  │                           │    │
│  └───────┬───────┘  │   status      │  └───────────────────────────┘    │
│          │          └───────────────┘                                    │
│          │                                                               │
│  ┌───────▼───────────────────────────────────────────────────────────┐  │
│  │                        API Service Layer                           │  │
│  │  - POST /api/detection/detect (multipart/form-data)               │  │
│  │  - GET /api/audit/history                                          │  │
│  │  - GET /api/products                                               │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │ HTTP / REST API
                                 │ (Image Upload)
┌────────────────────────────────▼────────────────────────────────────────┐
│                         PYTHON BACKEND (FastAPI)                         │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                          API ENDPOINTS                            │   │
│  │                                                                   │   │
│  │  POST /api/detection/detect     ← Receive image, detect products │   │
│  │       - multipart/form-data                                       │   │
│  │       - Returns: DetectionResult                                  │   │
│  │                                                                   │   │
│  │  POST /api/audit/run            ← Run audit comparison           │   │
│  │  GET  /api/audit/history        ← Audit history                  │   │
│  │  GET  /api/audit/stats          ← Statistics                     │   │
│  │  CRUD /api/products             ← Product management             │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                 │                                        │
│  ┌──────────────────────────────▼───────────────────────────────────┐   │
│  │                          SERVICES                                 │   │
│  │                                                                   │   │
│  │  ┌─────────────────────┐      ┌─────────────────────┐            │   │
│  │  │  DetectionService   │      │  AuditService       │            │   │
│  │  │                     │      │                     │            │   │
│  │  │  ┌───────────────┐  │      │  ┌───────────────┐  │            │   │
│  │  │  │ProductDetector│  │─────▶│  │ AuditEngine   │  │            │   │
│  │  │  │ (YOLO Model)  │  │      │  │               │  │            │   │
│  │  │  └───────────────┘  │      │  └───────────────┘  │            │   │
│  │  └─────────────────────┘      └─────────────────────┘            │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────────────┐
│                             DATABASE (MongoDB)                           │
│                                                                          │
│  ┌────────────────┐  ┌────────────────┐  ┌─────────────────────────┐    │
│  │ detections     │  │ audits         │  │ products                │    │
│  │                │  │                │  │                         │    │
│  │ - image_path   │  │ - audit_id     │  │ - name                  │    │
│  │ - detections[] │  │ - status       │  │ - expected_count        │    │
│  │ - timestamp    │  │ - match_rate   │  │ - category              │    │
│  │ - device_id    │  │ - discrepancies│  │ - barcode               │    │
│  └────────────────┘  └────────────────┘  └─────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Mobile App** | Flutter (Dart) |
| **ML Framework** | YOLOv8 (Ultralytics), PyTorch |
| **Computer Vision** | OpenCV, NumPy |
| **Backend** | FastAPI, Python |
| **Database** | MongoDB + Motor (async) |
| **Containerization** | Docker Compose |

## Project Structure

```
inventory_project/
├── mobile/                     # Flutter Mobile App
│   ├── lib/
│   │   ├── main.dart
│   │   ├── screens/            # UI screens
│   │   │   ├── camera_screen.dart
│   │   │   ├── results_screen.dart
│   │   │   └── history_screen.dart
│   │   ├── services/           # API service
│   │   │   └── api_service.dart
│   │   ├── models/             # Data models
│   │   │   ├── detection.dart
│   │   │   └── audit.dart
│   │   └── widgets/            # Reusable widgets
│   └── pubspec.yaml
│
├── backend/                    # Python FastAPI Backend
│   └── app/
│       ├── main.py
│       ├── config.py
│       ├── database.py
│       ├── models/
│       ├── routes/
│       └── services/
│
├── src/                        # ML Source Code
│   ├── data/                   # Data preprocessing
│   ├── training/               # Model training
│   ├── inference/              # Detection & Audit
│   └── utils/                  # Utilities
│
├── data/                       # Dataset
├── models/                     # Model weights & configs
├── tests/                      # Unit tests
└── docker-compose.yml
```

## API Endpoints

### Main Endpoint: Image Upload

```
POST /api/detection/detect
Content-Type: multipart/form-data

Request:
  - file: image (JPEG/PNG)
  - location: string (optional)
  - device_id: string (optional)

Response:
{
  "image_path": "uploads/2024/img_001.jpg",
  "timestamp": "2024-01-15T10:30:00",
  "total_products": 15,
  "processing_time_ms": 245.5,
  "detections": [
    {
      "class_id": 0,
      "class_name": "coca_cola",
      "confidence": 0.95,
      "bbox": [100, 150, 200, 300]
    },
    ...
  ]
}
```

### All Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/detection/detect` | Upload image, detect products |
| GET | `/api/detection/history` | Detection history |
| POST | `/api/audit/run` | Run audit comparison |
| GET | `/api/audit/history` | Audit history |
| GET | `/api/audit/stats` | Audit statistics |
| GET | `/api/products/` | List products |
| POST | `/api/products/` | Create product |
| PUT | `/api/products/{name}` | Update product |
| DELETE | `/api/products/{name}` | Delete product |

---

# 6-Week Implementation Plan

## Week 1: Foundation Setup

### Backend
- [ ] Review and organize FastAPI project structure
- [ ] Configure MongoDB connection
- [ ] `/api/detection/detect` endpoint - accept multipart/form-data
- [ ] Image storage logic (uploads folder)
- [ ] CORS configuration for Flutter app

### Flutter App
- [ ] Create Flutter project (`flutter create`)
- [ ] Set up folder structure (screens, services, models, widgets)
- [ ] Add core dependencies:
  - `http` - API calls
  - `image_picker` - Camera/Gallery
  - `provider` - State management
- [ ] Configure basic navigation

### Deliverables:
- Backend: Image upload endpoint working
- Flutter: Project skeleton ready

---

## Week 2: Flutter UI & API Integration

### Flutter App
- [ ] Build **CameraScreen**:
  - Camera preview
  - Capture button
  - Gallery picker
- [ ] Create **ApiService** class:
  - `uploadImage(File image)` method
  - Base URL configuration
  - Error handling
- [ ] Loading indicators, error states

### Backend
- [ ] Complete detection endpoint
- [ ] Finalize response format
- [ ] Image validation (size, format)
- [ ] Health check endpoint

### Deliverables:
- Flutter app can capture and send images to backend
- Backend returns response (mock data acceptable)

---

## Week 3: ML Model Integration

### ML Pipeline
- [ ] Prepare dataset (if not available)
- [ ] Verify data augmentation pipeline
- [ ] Train YOLOv8 model or use pretrained
- [ ] Save model weights (`models/weights/`)

### Backend
- [ ] Integrate ProductDetector service
- [ ] Load YOLO model on startup
- [ ] Detection endpoint performs real inference
- [ ] Measure processing time

### Deliverables:
- YOLO model running on backend with real detection
- Flutter app receives actual detection results

---

## Week 4: Results Display & Audit System

### Flutter App
- [ ] Build **ResultsScreen**:
  - Display detection results
  - Draw bounding boxes (optional)
  - Product list with confidence scores
- [ ] Create **Detection model** class
- [ ] Audit result display UI

### Backend
- [ ] Integrate AuditEngine
- [ ] `/api/audit/run` endpoint
- [ ] Manage expected inventory
- [ ] Store audit results

### Deliverables:
- Detection results displayed beautifully in Flutter
- Audit system returns PASS/WARNING/FAIL status

---

## Week 5: History & Statistics

### Flutter App
- [ ] Build **HistoryScreen**:
  - Past detections
  - Past audits
  - Filters (date, status)
- [ ] Build **StatsWidget**:
  - Total audit count
  - Pass/Fail rate
  - Charts (optional)
- [ ] Pull-to-refresh
- [ ] Pagination

### Backend
- [ ] Optimize history endpoints
- [ ] Statistics endpoint
- [ ] Query filters (date range, status)

### Deliverables:
- Fully functional history and statistics section

---

## Week 6: Testing & Polish

### Testing
- [ ] Write/verify backend unit tests
- [ ] Flutter widget tests
- [ ] Integration tests (app -> backend)
- [ ] Edge case testing (large images, poor lighting, etc.)

### Optimization
- [ ] Image compression (Flutter side)
- [ ] API response time optimization
- [ ] Improve error handling
- [ ] Offline mode (optional)

### Documentation
- [ ] API documentation (Swagger/OpenAPI)
- [ ] Flutter app README
- [ ] Deployment guide

### Deliverables:
- Production-ready app
- All tests passing
- Documentation complete

---

## Weekly Summary

| Week | Backend | Flutter | ML |
|------|---------|---------|-----|
| 1 | API setup, Image upload | Project setup, Navigation | - |
| 2 | Endpoint completion | Camera UI, API service | - |
| 3 | Detector integration | - | Model training |
| 4 | Audit system | Results UI | - |
| 5 | History, Stats APIs | History, Stats UI | - |
| 6 | Testing, Optimization | Testing, Polish | Evaluation |

---

## Dependencies

### Flutter (pubspec.yaml)
```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0              # API calls
  image_picker: ^1.0.4      # Camera/Gallery
  provider: ^6.1.1          # State management
  intl: ^0.18.1             # Date formatting
  cached_network_image: ^3.3.0  # Image caching
  fl_chart: ^0.65.0         # Charts (optional)
```

### Python (requirements.txt)
```
fastapi>=0.104.0
uvicorn>=0.24.0
motor>=3.3.0
python-multipart>=0.0.6
ultralytics>=8.0.0
opencv-python>=4.8.0
numpy>=1.24.0
Pillow>=10.0.0
```

---

## Quick Start

### Backend
```bash
# Activate virtual environment
source inventory_env/bin/activate

# Start MongoDB
docker-compose up mongodb -d

# Start backend
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### Flutter App
```bash
cd mobile

# Install dependencies
flutter pub get

# Run app
flutter run

# Build APK
flutter build apk --release
```

### Docker (Full Stack)
```bash
docker-compose up --build
```
