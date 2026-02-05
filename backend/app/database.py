"""
MongoDB database connection using Motor (async driver).
"""

from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings


class Database:
    """MongoDB connection manager."""

    client: AsyncIOMotorClient = None
    db = None

    async def connect(self):
        """Connect to MongoDB."""
        self.client = AsyncIOMotorClient(settings.MONGODB_URI)
        self.db = self.client[settings.MONGODB_DB_NAME]
        print(f"Connected to MongoDB: {settings.MONGODB_DB_NAME}")

    async def disconnect(self):
        """Disconnect from MongoDB."""
        if self.client:
            self.client.close()
            print("Disconnected from MongoDB")

    def get_collection(self, name: str):
        """Get a MongoDB collection."""
        return self.db[name]


# Global database instance
database = Database()


# Collection accessors
def get_products_collection():
    return database.get_collection("products")


def get_detections_collection():
    return database.get_collection("detections")


def get_audits_collection():
    return database.get_collection("audits")
