"""
Product document model for MongoDB.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProductDocument(BaseModel):
    """Product document schema."""
    name: str
    category: str
    expected_count: int = 0
    location: str = ""
    sku: str = ""
    description: str = ""
    image_url: str = ""
    created_at: str = ""
    updated_at: str = ""

    def set_timestamps(self):
        now = datetime.now().isoformat()
        if not self.created_at:
            self.created_at = now
        self.updated_at = now
