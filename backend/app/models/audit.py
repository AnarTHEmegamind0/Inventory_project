"""
Audit result document model for MongoDB.
"""

from pydantic import BaseModel
from typing import List


class DiscrepancyItem(BaseModel):
    """Product discrepancy in audit."""
    product_name: str
    expected_count: int
    detected_count: int
    difference: int
    status: str


class AuditDocument(BaseModel):
    """Audit result document schema."""
    audit_id: str
    timestamp: str
    location: str
    status: str  # pass, fail, warning
    total_expected: int = 0
    total_detected: int = 0
    match_rate: float = 0.0
    discrepancies: List[DiscrepancyItem] = []
    missing_products: List[str] = []
    extra_products: List[str] = []
    notes: str = ""
