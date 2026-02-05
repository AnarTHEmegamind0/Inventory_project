"""Tests for the Audit Engine."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.inference.audit_engine import AuditEngine, AuditStatus


def test_audit_pass():
    """Test audit passes when inventory matches within tolerance."""
    engine = AuditEngine(tolerance=0.1)

    expected = {"cola": 10, "water": 10}
    detected = {"cola": 10, "water": 9}  # 10% tolerance

    result = engine.run_audit(expected, detected, location="Test Shelf")
    assert result.status == AuditStatus.PASS


def test_audit_warning():
    """Test audit warns when discrepancy is moderate."""
    engine = AuditEngine(tolerance=0.1, critical_threshold=0.3)

    expected = {"cola": 10, "water": 10}
    detected = {"cola": 10, "water": 8}  # 20% off

    result = engine.run_audit(expected, detected, location="Test Shelf")
    assert result.status == AuditStatus.WARNING


def test_audit_fail():
    """Test audit fails when product is completely missing."""
    engine = AuditEngine(tolerance=0.1)

    expected = {"cola": 10, "water": 10}
    detected = {"cola": 10}  # water completely missing

    result = engine.run_audit(expected, detected, location="Test Shelf")
    assert result.status == AuditStatus.FAIL
    assert "water" in result.missing_products


def test_audit_extra_products():
    """Test audit detects extra products not in expected inventory."""
    engine = AuditEngine(tolerance=0.1)

    expected = {"cola": 10}
    detected = {"cola": 10, "chips": 5}

    result = engine.run_audit(expected, detected, location="Test Shelf")
    assert "chips" in result.extra_products


def test_audit_match_rate():
    """Test match rate calculation."""
    engine = AuditEngine(tolerance=0.1)

    expected = {"cola": 10, "water": 10}
    detected = {"cola": 10, "water": 10}

    result = engine.run_audit(expected, detected, location="Test Shelf")
    assert result.match_rate == 1.0
    assert result.status == AuditStatus.PASS


def test_audit_report_generation():
    """Test report string generation."""
    engine = AuditEngine(tolerance=0.1)

    expected = {"cola": 10}
    detected = {"cola": 8}

    result = engine.run_audit(expected, detected, location="Aisle 1")
    report = engine.generate_report(result)
    assert "AUDIT REPORT" in report
    assert "Aisle 1" in report


if __name__ == "__main__":
    test_audit_pass()
    test_audit_warning()
    test_audit_fail()
    test_audit_extra_products()
    test_audit_match_rate()
    test_audit_report_generation()
    print("All audit engine tests passed!")
