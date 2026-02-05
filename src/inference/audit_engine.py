"""
Automated Audit Decision Engine.
Compares detected products against expected inventory to generate audit decisions.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class AuditStatus(str, Enum):
    """Audit decision statuses."""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    PENDING = "pending"


@dataclass
class ProductDiscrepancy:
    """Represents a discrepancy between expected and detected inventory."""
    product_name: str
    expected_count: int
    detected_count: int
    difference: int
    status: AuditStatus


@dataclass
class AuditResult:
    """Complete audit result."""
    audit_id: str
    timestamp: str
    location: str
    status: AuditStatus
    total_expected: int = 0
    total_detected: int = 0
    match_rate: float = 0.0
    discrepancies: List[ProductDiscrepancy] = field(default_factory=list)
    missing_products: List[str] = field(default_factory=list)
    extra_products: List[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary for MongoDB storage."""
        return {
            "audit_id": self.audit_id,
            "timestamp": self.timestamp,
            "location": self.location,
            "status": self.status.value,
            "total_expected": self.total_expected,
            "total_detected": self.total_detected,
            "match_rate": self.match_rate,
            "discrepancies": [
                {
                    "product_name": d.product_name,
                    "expected_count": d.expected_count,
                    "detected_count": d.detected_count,
                    "difference": d.difference,
                    "status": d.status.value,
                }
                for d in self.discrepancies
            ],
            "missing_products": self.missing_products,
            "extra_products": self.extra_products,
            "notes": self.notes,
        }


class AuditEngine:
    """
    Automated audit engine that compares detected products
    against expected inventory records.
    
    Usage:
        engine = AuditEngine(tolerance=0.1)
        
        expected = {"cola": 10, "water": 15, "juice": 8}
        detected = {"cola": 9, "water": 15, "juice": 6, "chips": 3}
        
        result = engine.run_audit(
            expected_inventory=expected,
            detected_products=detected,
            location="Shelf A-1"
        )
        
        print(result.status)  # AuditStatus.WARNING
    """

    def __init__(
        self,
        tolerance: float = 0.1,
        critical_threshold: float = 0.3,
    ):
        """
        Args:
            tolerance: Acceptable discrepancy ratio (0.1 = 10% tolerance)
            critical_threshold: Threshold for FAIL status (0.3 = 30% discrepancy)
        """
        self.tolerance = tolerance
        self.critical_threshold = critical_threshold
        self._audit_counter = 0

    def _generate_audit_id(self) -> str:
        """Generate unique audit ID."""
        self._audit_counter += 1
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"AUD-{timestamp}-{self._audit_counter:04d}"

    def run_audit(
        self,
        expected_inventory: Dict[str, int],
        detected_products: Dict[str, int],
        location: str = "Unknown",
    ) -> AuditResult:
        """
        Run audit comparison between expected and detected products.
        
        Args:
            expected_inventory: Dict of {product_name: expected_count}
            detected_products: Dict of {product_name: detected_count}
            location: Physical location identifier (shelf, aisle, etc.)
            
        Returns:
            AuditResult with complete audit analysis
        """
        audit_id = self._generate_audit_id()
        discrepancies = []
        missing_products = []
        extra_products = []

        all_products = set(list(expected_inventory.keys()) + list(detected_products.keys()))
        total_expected = sum(expected_inventory.values())
        total_detected = sum(detected_products.values())

        for product in all_products:
            expected = expected_inventory.get(product, 0)
            detected = detected_products.get(product, 0)
            difference = detected - expected

            # Determine status for this product
            if expected == 0 and detected > 0:
                status = AuditStatus.WARNING
                extra_products.append(product)
            elif expected > 0 and detected == 0:
                status = AuditStatus.FAIL
                missing_products.append(product)
            elif expected > 0:
                discrepancy_ratio = abs(difference) / expected
                if discrepancy_ratio <= self.tolerance:
                    status = AuditStatus.PASS
                elif discrepancy_ratio <= self.critical_threshold:
                    status = AuditStatus.WARNING
                else:
                    status = AuditStatus.FAIL
            else:
                status = AuditStatus.PASS

            if difference != 0:
                discrepancies.append(ProductDiscrepancy(
                    product_name=product,
                    expected_count=expected,
                    detected_count=detected,
                    difference=difference,
                    status=status,
                ))

        # Calculate overall match rate
        if total_expected > 0:
            match_rate = max(0, 1.0 - abs(total_detected - total_expected) / total_expected)
        else:
            match_rate = 1.0 if total_detected == 0 else 0.0

        # Determine overall audit status
        if any(d.status == AuditStatus.FAIL for d in discrepancies):
            overall_status = AuditStatus.FAIL
        elif any(d.status == AuditStatus.WARNING for d in discrepancies):
            overall_status = AuditStatus.WARNING
        else:
            overall_status = AuditStatus.PASS

        return AuditResult(
            audit_id=audit_id,
            timestamp=datetime.now().isoformat(),
            location=location,
            status=overall_status,
            total_expected=total_expected,
            total_detected=total_detected,
            match_rate=round(match_rate, 4),
            discrepancies=discrepancies,
            missing_products=missing_products,
            extra_products=extra_products,
        )

    def generate_report(self, result: AuditResult) -> str:
        """Generate human-readable audit report."""
        lines = [
            "=" * 50,
            f"AUDIT REPORT - {result.audit_id}",
            "=" * 50,
            f"Location:  {result.location}",
            f"Timestamp: {result.timestamp}",
            f"Status:    {result.status.value.upper()}",
            f"Match Rate: {result.match_rate * 100:.1f}%",
            "",
            f"Expected Total: {result.total_expected}",
            f"Detected Total: {result.total_detected}",
            "",
        ]

        if result.discrepancies:
            lines.append("DISCREPANCIES:")
            lines.append("-" * 40)
            for d in result.discrepancies:
                symbol = "+" if d.difference > 0 else ""
                lines.append(
                    f"  [{d.status.value.upper():7s}] {d.product_name}: "
                    f"expected={d.expected_count}, detected={d.detected_count} "
                    f"({symbol}{d.difference})"
                )

        if result.missing_products:
            lines.append(f"\nMISSING PRODUCTS: {', '.join(result.missing_products)}")

        if result.extra_products:
            lines.append(f"EXTRA PRODUCTS: {', '.join(result.extra_products)}")

        lines.append("=" * 50)
        return "\n".join(lines)


if __name__ == "__main__":
    # Example usage
    engine = AuditEngine(tolerance=0.1, critical_threshold=0.3)

    expected = {
        "coca_cola": 10,
        "pepsi": 8,
        "water_bottle": 15,
        "orange_juice": 6,
        "milk": 5,
    }

    detected = {
        "coca_cola": 9,
        "pepsi": 8,
        "water_bottle": 12,
        "orange_juice": 6,
        "chips": 3,
    }

    result = engine.run_audit(
        expected_inventory=expected,
        detected_products=detected,
        location="Shelf A-1, Aisle 3"
    )

    report = engine.generate_report(result)
    print(report)
