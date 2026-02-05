"""
Audit API endpoints.
Handles automated audit operations and audit history.
"""

from typing import Dict
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..database import get_audits_collection

router = APIRouter()


class AuditRequest(BaseModel):
    """Request body for running an audit."""
    expected_inventory: Dict[str, int]
    detected_products: Dict[str, int]
    location: str = "Unknown"
    tolerance: float = 0.1


@router.post("/run")
async def run_audit(request: AuditRequest):
    """
    Run an automated audit comparison.
    
    Compares expected inventory against detected products
    and generates an audit decision.
    """
    try:
        from src.inference.audit_engine import AuditEngine

        engine = AuditEngine(tolerance=request.tolerance)
        result = engine.run_audit(
            expected_inventory=request.expected_inventory,
            detected_products=request.detected_products,
            location=request.location,
        )

        audit_dict = result.to_dict()

        # Save to MongoDB
        collection = get_audits_collection()
        await collection.insert_one(audit_dict)

        # Remove MongoDB _id for response
        audit_dict.pop("_id", None)
        return audit_dict

    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="Audit engine not available. Check src/inference/audit_engine.py"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_audit_history(limit: int = 20, skip: int = 0):
    """Get audit history."""
    collection = get_audits_collection()
    cursor = collection.find({}, {"_id": 0}).sort("timestamp", -1).skip(skip).limit(limit)
    results = await cursor.to_list(length=limit)
    return {"results": results, "count": len(results)}


@router.get("/stats")
async def get_audit_stats():
    """Get audit statistics summary."""
    collection = get_audits_collection()

    total = await collection.count_documents({})
    passed = await collection.count_documents({"status": "pass"})
    failed = await collection.count_documents({"status": "fail"})
    warnings = await collection.count_documents({"status": "warning"})

    return {
        "total_audits": total,
        "passed": passed,
        "failed": failed,
        "warnings": warnings,
        "pass_rate": round(passed / max(total, 1), 4),
    }


@router.get("/{audit_id}")
async def get_audit(audit_id: str):
    """Get a specific audit result."""
    collection = get_audits_collection()
    result = await collection.find_one({"audit_id": audit_id}, {"_id": 0})
    if not result:
        raise HTTPException(status_code=404, detail="Audit not found")
    return result
