# Image-Based Product Recognition and Automated Audit Decision System

A machine learning system that uses YOLO object detection to recognize retail products from images and automatically generate inventory audit decisions.

## Tech Stack

- **ML**: YOLOv8 (Ultralytics), PyTorch, OpenCV
- **Backend**: FastAPI, Motor (MongoDB async driver)
- **Frontend**: React
- **Database**: MongoDB
- **Containerization**: Docker Compose

## Project Structure

```
inventory_project/
├── data/                   # Dataset (images, labels, splits)
├── models/                 # Model configs, weights, exports
├── src/                    # ML source code
│   ├── data/               # Preprocessing, augmentation, splitting
│   ├── training/           # YOLO training and evaluation
│   ├── inference/          # Detection and audit engine
│   └── utils/              # Visualization, logging
├── backend/                # FastAPI REST API
├── frontend/               # React dashboard
├── notebooks/              # Jupyter notebooks
└── tests/                  # Unit tests
```

## Quick Start

### 1. Setup Environment

```bash
# Activate virtual environment
source inventory_env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start MongoDB

```bash
# Using Docker
docker-compose up mongodb -d

# Or install MongoDB locally
```

### 3. Label Data

```bash
# Place raw images in data/raw/
# Run labelImg to annotate products
labelImg data/raw/ data/labeled/labels/ models/configs/dataset.yaml
```

### 4. Train Model

```bash
# Split dataset
python -m src.data.split_dataset

# Train YOLO model
python -m src.training.train
```

### 5. Run Backend

```bash
uvicorn backend.app.main:app --reload --port 8000
```

### 6. Run Frontend

```bash
cd frontend
npm install
npm start
```

### Docker (All Services)

```bash
docker-compose up --build
```

## API Endpoints

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
