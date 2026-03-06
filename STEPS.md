# STEPS.md — 100-Step Implementation Plan

> **Bachelor Thesis: Image-Based Product Recognition & Automated Audit Decision System**
>
> This file contains the EXACT sequence of steps to build the entire project from current state to production-ready.
> Each step is atomic — complete it fully before moving to the next.
> Steps are grouped into phases. DO NOT skip steps. DO NOT reorder.

---

## Progress Tracker

- ✅ = Done
- 🔄 = In Progress
- ⬜ = Not Started

---

## PHASE 1: BUG FIXES (Steps 1-5)

> Fix all known bugs in existing code before building anything new.
> **Consult Skills:** `python-testing`, `senior-computer-vision`

### Step 1 ⬜ — Fix `augment.py` typo
- **File:** `src/data/augment.py`
- **Line:** 1
- **Action:** Change `cla"""` to `"""`
- **Verify:** `python -c "from src.data.augment import augment_image; print('OK')"`

### Step 2 ⬜ — Fix `detector.py` variable assignment bug
- **File:** `src/inference/detector.py`
- **Line:** 172
- **Action:** Change `(text_w, text_h), _ = cv2.getFontSize = cv2.getTextSize(` to `(text_w, text_h), _ = cv2.getTextSize(`
- **Verify:** `python -c "from src.inference.detector import ProductDetector; print('OK')"`

### Step 3 ⬜ — Fix audit route to use AuditService instead of direct import
- **File:** `backend/app/routes/audit.py`
- **Action:** Replace the direct `from src.inference.audit_engine import AuditEngine` with `from ..services.audit_service import AuditService`. Update `run_audit()` to use `AuditService.run_audit()`.
- **Why:** Routes should call services, not ML code directly. This follows the ownership rules.
- **Verify:** `python -c "from backend.app.routes.audit import router; print('OK')"`

### Step 4 ⬜ — Fix detection route to use DetectionService
- **File:** `backend/app/routes/detection.py`
- **Action:** Remove the TODO placeholder (lines 43-57). Import and call `DetectionService.detect_from_file(str(file_path))`. If result is `None` (model not found), return the placeholder message. If result is valid, save to MongoDB and return.
- **Verify:** `python -c "from backend.app.routes.detection import router; print('OK')"`

### Step 5 ⬜ — Run all existing tests to confirm no regressions
- **Command:** `pytest tests/ -v`
- **Expected:** All tests in `test_audit_engine.py` pass. `test_detector.py` tests pass. `test_api.py` tests skip (no server running).
- **If tests fail:** Fix them before proceeding.

---

## PHASE 2: DATA COLLECTION & PREPARATION (Steps 6-20)

> Collect product images, label them, and prepare the dataset for YOLO training.
> **Consult Skills:** `senior-computer-vision`, `yolo`, `ml-model-training`, `computer-vision-opencv`

### Step 6 ⬜ — Define product classes for your dataset
- **File:** `models/configs/dataset.yaml`
- **Action:** Replace placeholder classes (`product_a`, `product_b`, `product_c`) with actual product names you will detect. Update `nc` to match the number of classes.
- **Example:**
  ```yaml
  nc: 5
  names:
    0: coca_cola
    1: pepsi
    2: water_bottle
    3: orange_juice
    4: milk
  ```
- **IMPORTANT:** Choose products that are visually distinct and available in your local retail store.

### Step 7 ⬜ — Collect raw product images
- **Action:** Take 50-100 photos per product class from a real retail store shelf. Use a phone camera. Include:
  - Different angles (straight, slight left, slight right)
  - Different lighting (natural, fluorescent, dim)
  - Different shelf arrangements (single product, crowded shelf, mixed products)
  - Multiple distances (close-up, medium, full shelf)
- **Output:** Save all images to `data/raw/` as `.jpg` files.
- **Minimum:** At least 300 total images across all classes.

### Step 8 ⬜ — Install LabelImg for annotation
- **Command:** `pip install labelImg` (already in requirements.txt)
- **Verify:** `labelImg --version` or just `labelImg` to see if it opens

### Step 9 ⬜ — Create label directories
- **Command:**
  ```bash
  mkdir -p data/labeled/images
  mkdir -p data/labeled/labels
  ```

### Step 10 ⬜ — Copy raw images to labeled/images
- **Command:** `cp data/raw/*.jpg data/labeled/images/`
- **Why:** Keep raw images untouched. Work on copies.

### Step 11 ⬜ — Label images using LabelImg
- **Command:** `labelImg data/labeled/images data/labeled/labels --autosave`
- **Settings in LabelImg:**
  - Change format to **YOLO** (not PascalVOC)
  - Save labels to `data/labeled/labels/`
  - Draw bounding boxes around each product
  - Assign the correct class name
- **CRITICAL:** Each `.jpg` must have a matching `.txt` label file in YOLO format:
  ```
  class_id x_center y_center width height
  ```
  where all values except class_id are normalized (0-1).
- **Goal:** Label ALL images. Every product in every image.

### Step 12 ⬜ — Verify label quality
- **Action:** Write a quick script or manually check 10-20 random label files to ensure:
  - Class IDs match `dataset.yaml`
  - Bounding boxes are tight around products
  - No missing labels (every visible product is labeled)
  - Format is correct (5 values per line, space-separated)
- **Command:** `head -5 data/labeled/labels/*.txt | head -30`

### Step 13 ⬜ — Count images and labels
- **Command:**
  ```bash
  echo "Images: $(ls data/labeled/images/*.jpg 2>/dev/null | wc -l)"
  echo "Labels: $(ls data/labeled/labels/*.txt 2>/dev/null | wc -l)"
  ```
- **Expected:** Both counts should be equal and ≥ 300.

### Step 14 ⬜ — Split dataset into train/val/test
- **Command:** `python -m src.data.split_dataset`
- **This runs `split_dataset()` with defaults:** 70% train, 20% val, 10% test, seed=42
- **Output:** Creates directories:
  ```
  data/splits/train/images/  data/splits/train/labels/
  data/splits/val/images/    data/splits/val/labels/
  data/splits/test/images/   data/splits/test/labels/
  ```
- **Verify:** Check file counts in each split directory.

### Step 15 ⬜ — Augment training data
- **Command:** `python -m src.data.augment`
- **This runs `augment_dataset()` with defaults:** 3 augmentations per image
- **Output:** Augmented images/labels in `data/augmented/`
- **Verify:** Check that augmented files exist and images look reasonable.

### Step 16 ⬜ — Copy augmented data into training set
- **Command:**
  ```bash
  cp data/augmented/images/*.jpg data/splits/train/images/
  cp data/augmented/labels/*.txt data/splits/train/labels/
  ```
- **Why:** Augmented data only goes into training, not validation or test.

### Step 17 ⬜ — Verify dataset.yaml paths are correct
- **File:** `models/configs/dataset.yaml`
- **Action:** Ensure `path` resolves correctly from where YOLO training will run. The current path is `../../data/splits` which is relative to the YAML file location. Verify this resolves to the actual `data/splits/` directory.
- **Verify:** `ls $(python -c "from pathlib import Path; print(Path('models/configs/dataset.yaml').parent / '../../data/splits')")`

### Step 18 ⬜ — Count final dataset split sizes
- **Command:**
  ```bash
  echo "Train: $(ls data/splits/train/images/ | wc -l) images"
  echo "Val:   $(ls data/splits/val/images/ | wc -l) images"
  echo "Test:  $(ls data/splits/test/images/ | wc -l) images"
  ```
- **Expected:** Train should have the most (original + augmented), val and test are original only.

### Step 19 ⬜ — Validate YOLO dataset format
- **Action:** Run a quick check that YOLO can load the dataset:
  ```python
  from ultralytics import YOLO
  model = YOLO("yolov8n.pt")
  # Dry run with 1 epoch to validate dataset format
  model.train(data="models/configs/dataset.yaml", epochs=1, imgsz=640, batch=2)
  ```
- **Expected:** Training starts without format errors. Can stop after 1 epoch.

### Step 20 ⬜ — Document dataset statistics
- **Action:** Create `data/README.md` with:
  - Number of classes and their names
  - Total images per class
  - Train/val/test split counts
  - Augmentation strategy used
  - Image resolution range
- **Why:** Thesis needs dataset documentation.

---

## PHASE 3: MODEL TRAINING (Steps 21-35)

> Train the YOLOv8 model on your product dataset.
> **Consult Skills:** `yolo`, `ml-model-training`, `machine-learning-engineer`, `senior-computer-vision`

### Step 21 ⬜ — Choose base model size
- **Decision:** Start with `yolov8n.pt` (nano) for fastest training. Can upgrade later.
- **File:** `src/training/train.py` → `model_name` parameter
- **Options:** `yolov8n.pt` (fastest) → `yolov8s.pt` → `yolov8m.pt` → `yolov8l.pt` (most accurate)

### Step 22 ⬜ — Configure hyperparameters
- **File:** `src/training/hyperparams.py`
- **Action:** Review and configure:
  - `epochs`: Start with 50 for initial run
  - `imgsz`: 640 (default, good balance)
  - `batch`: 16 if GPU has ≥ 8GB VRAM, else 8 or 4
  - `patience`: 20 (early stopping)
  - `device`: `"mps"` for Apple Silicon Mac, `"0"` for NVIDIA GPU, `"cpu"` for CPU

### Step 23 ⬜ — Start training run
- **Command:** `python -m src.training.train`
- **Expected output:** Training progress with loss values per epoch.
- **Output location:** `models/weights/product_detector/`
- **Wait time:** 30 min to several hours depending on dataset size and hardware.

### Step 24 ⬜ — Monitor training metrics
- **Action:** Watch for:
  - `box_loss` decreasing over epochs
  - `cls_loss` decreasing over epochs
  - `mAP50` increasing toward 0.7+
  - `mAP50-95` increasing toward 0.5+
  - Early stopping triggers if no improvement for 20 epochs

### Step 25 ⬜ — Verify best.pt was saved
- **Command:** `ls -la models/weights/product_detector/weights/`
- **Expected:** `best.pt` and `last.pt` files exist.
- **If missing:** Check training logs for errors.

### Step 26 ⬜ — Run model validation
- **Command:** `python -m src.training.evaluate`
- **Or in Python:**
  ```python
  from src.training.train import validate_model
  validate_model("models/weights/product_detector/weights/best.pt")
  ```
- **Record these metrics:** mAP50, mAP50-95, precision, recall

### Step 27 ⬜ — Test model on sample images
- **Command:**
  ```python
  from src.inference.detector import ProductDetector
  detector = ProductDetector("models/weights/product_detector/weights/best.pt")
  result = detector.detect("data/splits/test/images/<any_test_image>.jpg")
  print(f"Detected {result.total_products} products")
  for d in result.detections:
      print(f"  {d.class_name}: {d.confidence:.2f}")
  ```
- **Expected:** Correct product classes detected with confidence > 0.5.

### Step 28 ⬜ — Visualize detections on test images
- **Action:** Use `ProductDetector.draw_detections()` to save annotated images:
  ```python
  import cv2
  from src.inference.detector import ProductDetector
  
  detector = ProductDetector("models/weights/product_detector/weights/best.pt")
  img = cv2.imread("data/splits/test/images/<test_image>.jpg")
  result = detector.detect(img)
  annotated = detector.draw_detections(img, result)
  cv2.imwrite("data/test_result.jpg", annotated)
  ```
- **Why:** Visual verification of bounding box accuracy. Good for thesis figures.

### Step 29 ⬜ — Evaluate per-class performance
- **Action:** Check which product classes perform well and which struggle:
  ```python
  from ultralytics import YOLO
  model = YOLO("models/weights/product_detector/weights/best.pt")
  results = model.val(data="models/configs/dataset.yaml")
  # Per-class metrics available in results
  ```
- **If some classes have low mAP:** Collect more images for those classes and retrain.

### Step 30 ⬜ — (Optional) Try larger model if accuracy insufficient
- **Action:** If mAP50 < 0.7, try `yolov8s.pt` or `yolov8m.pt`:
  ```python
  from src.training.train import train_model
  train_model(model_name="yolov8s.pt", epochs=100)
  ```
- **Compare:** mAP50, mAP50-95, and inference speed.

### Step 31 ⬜ — (Optional) Tune confidence and IOU thresholds
- **Action:** Try different threshold values on validation set:
  ```python
  detector = ProductDetector("models/weights/product_detector/weights/best.pt", conf_threshold=0.3, iou_threshold=0.5)
  ```
- **Goal:** Find the threshold that gives best balance of precision/recall.

### Step 32 ⬜ — Update `.env.example` with final model path
- **File:** `.env.example`
- **Action:** Ensure `MODEL_PATH` points to the correct `best.pt` location.
- **Value:** `MODEL_PATH=models/weights/product_detector/weights/best.pt`

### Step 33 ⬜ — Create `.env` from `.env.example`
- **Command:** `cp .env.example .env`
- **Action:** Review all values in `.env` and update any that need to change.

### Step 34 ⬜ — Document training results
- **Action:** Create `models/README.md` with:
  - Base model used (e.g., yolov8n.pt)
  - Final mAP50, mAP50-95, precision, recall
  - Number of epochs trained
  - Training time
  - Hardware used
  - Per-class performance table
- **Why:** Required for thesis methodology chapter.

### Step 35 ⬜ — Commit trained model config (not weights)
- **Action:** Ensure `models/weights/` is in `.gitignore` but `models/configs/dataset.yaml` is committed.
- **Command:** `git add models/configs/dataset.yaml models/README.md`

---

## PHASE 4: BACKEND INTEGRATION (Steps 36-55)

> Wire up the trained model to the FastAPI backend for real-time detection.
> **Consult Skills:** `fastapi-expert`, `mongodb`, `python-testing`

### Step 36 ⬜ — Start MongoDB
- **Command:** `docker-compose up mongodb -d`
- **Verify:** `docker ps` shows `inventory_mongodb` running on port 27017.

### Step 37 ⬜ — Test MongoDB connection
- **Command:**
  ```python
  python -c "
  import asyncio
  from motor.motor_asyncio import AsyncIOMotorClient
  async def test():
      client = AsyncIOMotorClient('mongodb://localhost:27017')
      db = client['inventory_audit']
      await db.list_collection_names()
      print('MongoDB OK')
  asyncio.run(test())
  "
  ```

### Step 38 ⬜ — Update `config.py` to load `.env` file
- **File:** `backend/app/config.py`
- **Action:** Add `python-dotenv` loading at the top:
  ```python
  from dotenv import load_dotenv
  load_dotenv()
  ```
- **Why:** Currently uses `os.getenv()` but `.env` file won't be loaded unless `load_dotenv()` is called.

### Step 39 ⬜ — Verify DetectionService finds the model
- **Command:**
  ```python
  python -c "
  from backend.app.services.detection_service import DetectionService
  detector = DetectionService.get_detector()
  print('Detector loaded!' if detector else 'Model not found')
  "
  ```
- **Expected:** "Detector loaded!" if `MODEL_PATH` in `.env` points to existing `best.pt`.

### Step 40 ⬜ — Update detection route to use DetectionService properly
- **File:** `backend/app/routes/detection.py`
- **Action:** Replace the placeholder (lines 43-57) with:
  ```python
  from ..services.detection_service import DetectionService
  
  # In detect_products():
  result = DetectionService.detect_from_file(str(file_path))
  if result is None:
      result = {
          "image_path": str(file_path),
          "timestamp": datetime.now().isoformat(),
          "detections": [],
          "total_products": 0,
          "processing_time_ms": 0,
          "message": "Model not loaded. Train a model first.",
      }
  ```
- **Also add:** `detection_id` field (UUID) to the result for later retrieval.

### Step 41 ⬜ — Add detection_id to detection results
- **File:** `backend/app/routes/detection.py`
- **Action:** Generate a unique `detection_id` for each detection:
  ```python
  import uuid
  result["detection_id"] = str(uuid.uuid4())
  ```
- **Why:** The `GET /api/detection/{detection_id}` endpoint needs this field.

### Step 42 ⬜ — Update audit route to use AuditService
- **File:** `backend/app/routes/audit.py`
- **Action:** Replace the direct `AuditEngine` import with `AuditService`:
  ```python
  from ..services.audit_service import AuditService
  
  # In run_audit():
  audit_dict = AuditService.run_audit(
      expected=request.expected_inventory,
      detected=request.detected_products,
      location=request.location,
  )
  ```

### Step 43 ⬜ — Start the backend server
- **Command:** `source inventory_env/bin/activate && uvicorn backend.app.main:app --reload --port 8000`
- **Verify:** `curl http://localhost:8000/health` returns `{"status": "healthy"}`

### Step 44 ⬜ — Test detection endpoint with real image
- **Command:**
  ```bash
  curl -X POST http://localhost:8000/api/detection/detect \
    -F "file=@data/splits/test/images/<test_image>.jpg"
  ```
- **Expected:** JSON with `detections[]` array containing detected products.

### Step 45 ⬜ — Test audit endpoint with sample data
- **Command:**
  ```bash
  curl -X POST http://localhost:8000/api/audit/run \
    -H "Content-Type: application/json" \
    -d '{"expected_inventory": {"cola": 10, "water": 5}, "detected_products": {"cola": 9, "water": 5}, "location": "Shelf A"}'
  ```
- **Expected:** JSON with `status`, `match_rate`, `discrepancies`.

### Step 46 ⬜ — Test product CRUD endpoints
- **Commands:**
  ```bash
  # Create
  curl -X POST http://localhost:8000/api/products/ \
    -H "Content-Type: application/json" \
    -d '{"name": "coca_cola", "category": "beverages", "expected_count": 10}'
  
  # List
  curl http://localhost:8000/api/products/
  
  # Get one
  curl http://localhost:8000/api/products/coca_cola
  
  # Delete
  curl -X DELETE http://localhost:8000/api/products/coca_cola
  ```

### Step 47 ⬜ — Test detection history endpoint
- **Command:** `curl http://localhost:8000/api/detection/history`
- **Expected:** JSON with `results` array (should contain the detection from step 44).

### Step 48 ⬜ — Test audit history and stats endpoints
- **Commands:**
  ```bash
  curl http://localhost:8000/api/audit/history
  curl http://localhost:8000/api/audit/stats
  ```

### Step 49 ⬜ — Add input validation to detection route
- **File:** `backend/app/routes/detection.py`
- **Action:** Add file size check:
  ```python
  contents = await file.read()
  if len(contents) > settings.MAX_UPLOAD_SIZE:
      raise HTTPException(400, "File too large")
  await file.seek(0)  # Reset file position
  ```

### Step 50 ⬜ — Add error handling for model loading failures
- **File:** `backend/app/services/detection_service.py`
- **Action:** Wrap model loading in try/except. Log errors. Return None gracefully.

### Step 51 ⬜ — Refactor tests to use FastAPI TestClient
- **File:** `tests/test_api.py`
- **Action:** Rewrite all tests to use:
  ```python
  from fastapi.testclient import TestClient
  from backend.app.main import app
  client = TestClient(app)
  ```
- **Remove:** `import requests` and hard-coded URLs.

### Step 52 ⬜ — Add new tests for detection endpoint
- **File:** `tests/test_api.py`
- **Action:** Add tests for:
  - Upload valid image → 200
  - Upload invalid file type → 400
  - Upload too-large file → 400
  - Get detection history → 200

### Step 53 ⬜ — Add new tests for audit endpoint
- **File:** `tests/test_api.py`
- **Action:** Add tests for:
  - Run audit with valid data → 200
  - Run audit with empty data → 200 (should pass with no discrepancies)
  - Get audit stats → 200

### Step 54 ⬜ — Run all tests
- **Command:** `pytest tests/ -v`
- **Expected:** ALL tests pass.

### Step 55 ⬜ — Test Swagger docs
- **Action:** Open `http://localhost:8000/docs` in browser.
- **Verify:** All endpoints are listed with correct request/response schemas.
- **Try:** Execute a detection from the Swagger UI.

---

## PHASE 5: FRONTEND — REACT UPGRADE & UI (Steps 56-80)

> Rebuild the frontend with modern React patterns and beautiful UI.
> **Consult Skills:** `react-vite-expert`

### Step 56 ⬜ — Install frontend dependencies
- **Command:** `cd frontend && npm install`
- **Verify:** `npm start` runs without errors.

### Step 57 ⬜ — (Optional) Migrate from CRA to Vite
- **Action:** If you want faster dev experience:
  1. Install Vite: `npm install vite @vitejs/plugin-react`
  2. Create `vite.config.js`
  3. Update `package.json` scripts
  4. Rename env vars from `REACT_APP_*` to `VITE_*`
  5. Remove `react-scripts`
- **Consult:** `.agents/skills/react-vite-expert/SKILL.md` for detailed migration guide.

### Step 58 ⬜ — Set up environment variables for frontend
- **Action:** Create `frontend/.env`:
  ```
  REACT_APP_API_URL=http://localhost:8000/api
  ```
  Or if using Vite: `VITE_API_URL=http://localhost:8000/api`

### Step 59 ⬜ — Review and understand existing frontend pages
- **Action:** Read all 4 page components to understand current state:
  - `Dashboard.js` — what stats does it show?
  - `Upload.js` — how does file upload work?
  - `Products.js` — what CRUD operations exist?
  - `AuditReport.js` — how are results displayed?

### Step 60 ⬜ — Add CSS framework or design system
- **Action:** Choose one:
  - **Option A:** Install Tailwind CSS: `npm install tailwindcss @tailwindcss/vite` (if using Vite)
  - **Option B:** Use CSS Modules (already supported by CRA)
  - **Option C:** Keep vanilla CSS in `App.css`
- **Recommendation:** Tailwind for speed, CSS Modules for simplicity.

### Step 61 ⬜ — Create responsive layout component
- **File:** `frontend/src/components/Layout.js`
- **Action:** Create a layout wrapper with:
  - Top navigation bar with app title
  - Sidebar with navigation links (Dashboard, Upload, Products, Reports)
  - Main content area
  - Responsive: sidebar collapses on mobile

### Step 62 ⬜ — Create reusable Card component
- **File:** `frontend/src/components/Card.js`
- **Action:** A card container with title, subtitle, and body. Used across all pages.

### Step 63 ⬜ — Create reusable StatusBadge component
- **File:** `frontend/src/components/StatusBadge.js`
- **Action:** Colored badge showing PASS (green), WARNING (yellow), FAIL (red).

### Step 64 ⬜ — Create Loading and Error components
- **File:** `frontend/src/components/Loading.js`, `frontend/src/components/Error.js`
- **Action:** Spinner for loading state, error message with retry button.

### Step 65 ⬜ — Redesign Dashboard page
- **File:** `frontend/src/pages/Dashboard.js`
- **Action:**
  - Top row: 4 stat cards (Total Audits, Pass Rate, Warnings, Fails)
  - Middle: Pie chart or bar chart of audit statuses (use Recharts)
  - Bottom: Recent detections list with timestamps
- **Data sources:** `getAuditStats()`, `getDetectionHistory()`, `getAuditHistory()`

### Step 66 ⬜ — Redesign Upload page
- **File:** `frontend/src/pages/Upload.js`
- **Action:**
  - Drag-and-drop zone for image upload
  - Image preview before upload
  - Upload button with progress indicator
  - After upload: show detection results inline
  - Display detected products with confidence scores
  - "Run Audit" button to trigger audit on the detection result

### Step 67 ⬜ — Redesign Products page
- **File:** `frontend/src/pages/Products.js`
- **Action:**
  - Table view with columns: Name, Category, Expected Count, Location, SKU
  - "Add Product" button → modal form
  - Edit/Delete buttons per row
  - Category filter dropdown
  - Search by name

### Step 68 ⬜ — Redesign AuditReport page
- **File:** `frontend/src/pages/AuditReport.js`
- **Action:**
  - Overall status badge (large, centered)
  - Match rate percentage (visual progress bar)
  - Discrepancies table: Product, Expected, Detected, Difference, Status
  - Missing products list (red)
  - Extra products list (yellow)
  - Full audit report text (expandable)

### Step 69 ⬜ — Add audit history page
- **File:** `frontend/src/pages/AuditHistory.js`
- **Action:** List of past audits with:
  - Date, Location, Status badge, Match Rate
  - Click to view full audit report
  - Filter by status (Pass/Warning/Fail)
  - Pagination

### Step 70 ⬜ — Add detection history page
- **File:** `frontend/src/pages/DetectionHistory.js`
- **Action:** List of past detections with:
  - Thumbnail of uploaded image
  - Total products detected
  - Processing time
  - Click to view full detection details

### Step 71 ⬜ — Update App.js routing
- **File:** `frontend/src/App.js`
- **Action:** Add routes for all pages:
  ```jsx
  <Route path="/" element={<Dashboard />} />
  <Route path="/upload" element={<Upload />} />
  <Route path="/products" element={<Products />} />
  <Route path="/audit" element={<AuditReport />} />
  <Route path="/audit/history" element={<AuditHistory />} />
  <Route path="/detection/history" element={<DetectionHistory />} />
  ```

### Step 72 ⬜ — Add updateProduct to api.js
- **File:** `frontend/src/services/api.js`
- **Action:** Add missing API function:
  ```javascript
  export const updateProduct = async (name, product) => {
    const res = await api.put(`/products/${name}`, product);
    return res.data;
  };
  ```

### Step 73 ⬜ — Add getDetection (single) to api.js
- **File:** `frontend/src/services/api.js`
- **Action:**
  ```javascript
  export const getDetection = async (detectionId) => {
    const res = await api.get(`/detection/${detectionId}`);
    return res.data;
  };
  ```

### Step 74 ⬜ — Add getAudit (single) to api.js
- **File:** `frontend/src/services/api.js`
- **Action:**
  ```javascript
  export const getAudit = async (auditId) => {
    const res = await api.get(`/audit/${auditId}`);
    return res.data;
  };
  ```

### Step 75 ⬜ — Add loading states to all pages
- **Action:** Every page that fetches data should show:
  - Loading spinner while fetching
  - Error message if fetch fails
  - Empty state message if no data
- **Pattern:** `const [loading, setLoading] = useState(true);`

### Step 76 ⬜ — Add error handling to all API calls
- **Action:** Wrap all API calls in try/catch with user-friendly error messages:
  ```javascript
  try {
    const data = await getProducts();
    setProducts(data.products);
  } catch (error) {
    setError(error.response?.data?.detail || "Failed to load products");
  }
  ```

### Step 77 ⬜ — Test frontend-backend integration
- **Action:** With both backend and frontend running:
  1. Upload an image on Upload page → see detection results
  2. Create a product on Products page → verify it appears in list
  3. Run an audit → see results on Audit page
  4. Check Dashboard → stats should reflect the above actions

### Step 78 ⬜ — Add responsive design for mobile
- **Action:** Test all pages at mobile width (375px). Fix any layout issues.
- **Key:** Upload page should work on mobile too.

### Step 79 ⬜ — Add dark mode (optional but recommended)
- **Action:** Add a dark mode toggle in the navigation.
- **Implementation:** CSS custom properties (variables) for colors, toggle body class.

### Step 80 ⬜ — Polish UI animations and transitions
- **Action:** Add:
  - Fade-in animations for page loads
  - Hover effects on cards and buttons
  - Smooth transitions for status badge colors
  - Upload progress bar animation

---

## PHASE 6: INTEGRATION & END-TO-END FLOW (Steps 81-90)

> Connect the full pipeline: Upload → Detect → Audit → Report.
> **Consult Skills:** `fastapi-expert`, `react-vite-expert`

### Step 81 ⬜ — Create end-to-end flow on Upload page
- **Action:** After image upload and detection, automatically:
  1. Show detected products with counts (e.g., "coca_cola: 9, water: 12")
  2. Fetch expected inventory from MongoDB
  3. Show "Run Audit" button
  4. On click: POST to `/api/audit/run` with expected vs detected
  5. Display audit result inline (status, match rate, discrepancies)
  6. "View Full Report" link → navigate to AuditReport page

### Step 82 ⬜ — Add auto-populate expected inventory for audit
- **File:** `backend/app/routes/audit.py`
- **Action:** Add a new endpoint `POST /api/audit/auto-run` that:
  1. Takes a `detection_id`
  2. Fetches detections from MongoDB
  3. Fetches all expected products from MongoDB
  4. Automatically runs audit comparison
  5. Returns AuditResult
- **Why:** Frontend shouldn't need to manually pass expected_inventory.

### Step 83 ⬜ — Update api.js with autoRunAudit
- **File:** `frontend/src/services/api.js`
- **Action:**
  ```javascript
  export const autoRunAudit = async (detectionId) => {
    const res = await api.post('/audit/auto-run', { detection_id: detectionId });
    return res.data;
  };
  ```

### Step 84 ⬜ — Test full end-to-end flow
- **Action:**
  1. Start MongoDB: `docker-compose up mongodb -d`
  2. Start backend: `uvicorn backend.app.main:app --reload --port 8000`
  3. Start frontend: `cd frontend && npm start`
  4. Add products (at least 3) via Products page
  5. Upload a shelf image via Upload page
  6. See detection results
  7. Click "Run Audit"
  8. See audit result (PASS/WARNING/FAIL)
  9. Check Dashboard for updated stats
  10. Check Audit History for the new audit

### Step 85 ⬜ — Handle edge cases
- **Action:** Test and handle:
  - Upload image with no products detected → should show "No products detected"
  - Run audit with no expected products defined → should show warning
  - Network error during upload → show retry button
  - Very large image → should compress or reject gracefully

### Step 86 ⬜ — Add image annotation on detection result
- **Action:** After detection, display the uploaded image with bounding boxes drawn on it.
- **Backend:** Add endpoint `GET /api/detection/{detection_id}/annotated` that returns annotated image.
- **Or Frontend:** Draw bounding boxes on canvas using detection coordinates.

### Step 87 ⬜ — Add real-time detection counter on Upload page
- **Action:** Show a count badge as products are detected:
  - "🔍 15 products detected in 245ms"
  - Per-product breakdown with icons

### Step 88 ⬜ — Add inventory summary endpoint to dashboard
- **Action:** Dashboard should call `GET /api/products/inventory/summary` and show per-category breakdown.

### Step 89 ⬜ — Test with multiple audit runs
- **Action:** Upload 5+ different images, run audits, verify:
  - History pages show all runs
  - Stats are calculated correctly
  - Dashboard charts update

### Step 90 ⬜ — Run full regression tests
- **Command:** `pytest tests/ -v`
- **Expected:** ALL tests pass with no regressions.

---

## PHASE 7: DOCKER & DEPLOYMENT (Steps 91-95)

> Containerize everything for easy deployment and thesis demo.
> **Consult Skills:** `docker-patterns`

### Step 91 ⬜ — Update backend Dockerfile
- **File:** `backend/Dockerfile`
- **Action:** Ensure it:
  - Installs all Python dependencies
  - Copies the `src/` directory (needed for ML inference)
  - Copies the `models/` directory (for YOLO weights)
  - Exposes port 8000
  - Sets correct working directory

### Step 92 ⬜ — Update frontend Dockerfile
- **File:** `frontend/Dockerfile`
- **Action:** Ensure it:
  - Installs npm dependencies
  - Builds the production bundle
  - Serves with a static file server (nginx or serve)

### Step 93 ⬜ — Test full Docker stack
- **Command:** `docker-compose up --build`
- **Verify:**
  - `http://localhost:3000` → Frontend loads
  - `http://localhost:8000/docs` → Swagger docs load
  - Upload image through frontend → detection works
  - Run audit → results display

### Step 94 ⬜ — Add health check to docker-compose
- **File:** `docker-compose.yml`
- **Action:** Add health checks for backend and MongoDB:
  ```yaml
  backend:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
  ```

### Step 95 ⬜ — Document deployment process
- **File:** `DEPLOY.md`
- **Action:** Write instructions for:
  - Prerequisites (Docker, Docker Compose)
  - How to build and run
  - Environment variable configuration
  - How to access the application
  - Troubleshooting common issues

---

## PHASE 8: TESTING & DOCUMENTATION (Steps 96-100)

> Final testing, documentation, and thesis preparation.
> **Consult Skills:** `python-testing`

### Step 96 ⬜ — Write comprehensive backend tests
- **Action:** Ensure test coverage for:
  - All API endpoints (using TestClient)
  - Edge cases (empty data, invalid inputs, large files)
  - Audit engine (all status combinations)
  - Detection service (model loaded vs not loaded)
- **Target:** 80%+ code coverage
- **Command:** `pytest tests/ -v --cov=backend --cov=src`

### Step 97 ⬜ — Run final end-to-end test
- **Action:** Complete walkthrough of the entire system:
  1. Start fresh (empty database)
  2. Add products
  3. Upload images
  4. View detections
  5. Run audits
  6. Check history
  7. Check stats
  8. All features working
- **Record:** Take screenshots for thesis.

### Step 98 ⬜ — Create API documentation
- **Action:**
  - Export Swagger/OpenAPI spec: `curl http://localhost:8000/openapi.json > docs/api-spec.json`
  - Take screenshots of Swagger UI for thesis
  - Write API usage examples in README

### Step 99 ⬜ — Update README.md
- **File:** `README.md`
- **Action:** Update with:
  - Actual product classes (not placeholders)
  - Real model performance metrics
  - Screenshots of the working application
  - Updated quick start instructions
  - Thesis abstract/description

### Step 100 ⬜ — Final commit and tag
- **Commands:**
  ```bash
  git add -A
  git commit -m "v1.0.0: Complete inventory audit system"
  git tag -a v1.0.0 -m "Bachelor thesis final version"
  git push origin main --tags
  ```
- **🎉 DONE! Your bachelor thesis project is complete.**

---

## Quick Reference: Phase Summary

| Phase | Steps | Description | Key Skills |
|-------|-------|-------------|------------|
| 1. Bug Fixes | 1-5 | Fix known bugs in existing code | `python-testing` |
| 2. Data Prep | 6-20 | Collect, label, augment, split dataset | `yolo`, `senior-computer-vision` |
| 3. Training | 21-35 | Train YOLOv8 model | `ml-model-training`, `yolo` |
| 4. Backend | 36-55 | Wire model to API, test endpoints | `fastapi-expert`, `mongodb` |
| 5. Frontend | 56-80 | Rebuild React UI with modern design | `react-vite-expert` |
| 6. Integration | 81-90 | End-to-end flow, edge cases | All skills |
| 7. Docker | 91-95 | Containerize and deploy | `docker-patterns` |
| 8. Final | 96-100 | Testing, documentation, submission | `python-testing` |
