"""
Detection API endpoints.
Handles image upload and product detection.
"""

import shutil
from pathlib import Path
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, HTTPException
from ..config import settings
from ..database import get_detections_collection

router = APIRouter()


@router.post("/detect")
async def detect_products(file: UploadFile = File(...)):
    """
    Upload an image and detect products.
    
    Returns detection results with bounding boxes and class labels.
    """
    # Validate file type
    allowed_types = {"image/jpeg", "image/png", "image/bmp"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file.content_type} not supported. Use JPEG, PNG, or BMP."
        )

    # Save uploaded file
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = upload_dir / filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # TODO: Initialize detector once at startup (in lifespan)
        # from src.inference.detector import ProductDetector
        # detector = ProductDetector(settings.MODEL_PATH)
        # result = detector.detect(str(file_path))

        # Placeholder response until model is trained
        result = {
            "image_path": str(file_path),
            "timestamp": datetime.now().isoformat(),
            "detections": [],
            "total_products": 0,
            "processing_time_ms": 0,
            "message": "Model not loaded yet. Train a model first.",
        }

        # Save to MongoDB
        collection = get_detections_collection()
        await collection.insert_one(result)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_detection_history(limit: int = 20, skip: int = 0):
    """Get detection history from database."""
    collection = get_detections_collection()
    cursor = collection.find({}, {"_id": 0}).sort("timestamp", -1).skip(skip).limit(limit)
    results = await cursor.to_list(length=limit)
    return {"results": results, "count": len(results)}


@router.get("/{detection_id}")
async def get_detection(detection_id: str):
    """Get a specific detection result."""
    collection = get_detections_collection()
    result = await collection.find_one({"detection_id": detection_id}, {"_id": 0})
    if not result:
        raise HTTPException(status_code=404, detail="Detection not found")
    return result
