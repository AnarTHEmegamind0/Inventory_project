"""
Audit business logic service.
Handles audit operations and reporting.
"""

from typing import Dict
from src.inference.audit_engine import AuditEngine, AuditResult
from ..config import settings


class AuditService:
    """Manages audit operations."""

    _engine = None

    @classmethod
    def get_engine(cls) -> AuditEngine:
        """Get or initialize the audit engine (singleton)."""
        if cls._engine is None:
            cls._engine = AuditEngine(
                tolerance=settings.AUDIT_TOLERANCE,
                critical_threshold=settings.AUDIT_CRITICAL_THRESHOLD,
            )
        return cls._engine

    @classmethod
    def run_audit(
        cls,
        expected: Dict[str, int],
        detected: Dict[str, int],
        location: str = "Unknown"
    ) -> dict:
        """Run audit and return result as dictionary."""
        engine = cls.get_engine()
        result = engine.run_audit(expected, detected, location)
        return result.to_dict()

    @classmethod
    def generate_report(cls, result: AuditResult) -> str:
        """Generate human-readable audit report."""
        engine = cls.get_engine()
        return engine.generate_report(result)
