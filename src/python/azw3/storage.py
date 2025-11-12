"""
Storage backends for different storage systems.
Stack-agnostic storage abstraction.
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from .config import StorageConfig

logger = logging.getLogger(__name__)


class StorageBackend(ABC):
    """Base class for storage backends."""
    
    @abstractmethod
    async def write(self, layer: str, data: List[Dict[str, Any]]):
        """Write data to storage."""
        pass
    
    @abstractmethod
    async def read(self, layer: str, limit: int = 100) -> Optional[List[Dict[str, Any]]]:
        """Read data from storage."""
        pass


class S3Storage(StorageBackend):
    """AWS S3 storage backend."""
    
    def __init__(self, config: StorageConfig):
        self.config = config
        self.bucket = config.bucket
        self.region = config.region or "us-east-1"
        self._client = None
    
    def _get_client(self):
        """Get S3 client (lazy initialization)."""
        if self._client is None:
            try:
                import boto3
                self._client = boto3.client("s3", region_name=self.region)
            except ImportError:
                raise ImportError("boto3 not installed. Install with: pip install boto3")
        return self._client
    
    async def write(self, layer: str, data: List[Dict[str, Any]]):
        """Write data to S3."""
        import json
        from datetime import datetime
        
        client = self._get_client()
        key = f"{layer}/{datetime.utcnow().isoformat()}.json"
        
        # In production, this would be async
        client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=json.dumps(data),
            ContentType="application/json"
        )
        
        logger.debug(f"Wrote {len(data)} records to S3: {key}")
    
    async def read(self, layer: str, limit: int = 100) -> Optional[List[Dict[str, Any]]]:
        """Read data from S3."""
        import json
        
        client = self._get_client()
        # Placeholder - in production would list and read objects
        return []


class PostgreSQLStorage(StorageBackend):
    """PostgreSQL storage backend."""
    
    def __init__(self, config: StorageConfig):
        self.config = config
        self.connection_string = config.connection_string
        self._connection = None
    
    def _get_connection(self):
        """Get database connection (lazy initialization)."""
        if self._connection is None:
            try:
                import psycopg2
                self._connection = psycopg2.connect(self.connection_string)
            except ImportError:
                raise ImportError("psycopg2 not installed. Install with: pip install psycopg2-binary")
        return self._connection
    
    async def write(self, layer: str, data: List[Dict[str, Any]]):
        """Write data to PostgreSQL."""
        # Placeholder - in production would use asyncpg or similar
        logger.debug(f"Would write {len(data)} records to PostgreSQL {layer} table")
    
    async def read(self, layer: str, limit: int = 100) -> Optional[List[Dict[str, Any]]]:
        """Read data from PostgreSQL."""
        # Placeholder
        return []


class MongoDBStorage(StorageBackend):
    """MongoDB storage backend."""
    
    def __init__(self, config: StorageConfig):
        self.config = config
        self.connection_string = config.connection_string
        self._client = None
    
    def _get_client(self):
        """Get MongoDB client (lazy initialization)."""
        if self._client is None:
            try:
                from pymongo import MongoClient
                self._client = MongoClient(self.connection_string)
            except ImportError:
                raise ImportError("pymongo not installed. Install with: pip install pymongo")
        return self._client
    
    async def write(self, layer: str, data: List[Dict[str, Any]]):
        """Write data to MongoDB."""
        client = self._get_client()
        db = client.get_database("azw3")
        collection = db.get_collection(layer)
        
        # In production, this would be async
        collection.insert_many(data)
        
        logger.debug(f"Wrote {len(data)} records to MongoDB {layer} collection")
    
    async def read(self, layer: str, limit: int = 100) -> Optional[List[Dict[str, Any]]]:
        """Read data from MongoDB."""
        client = self._get_client()
        db = client.get_database("azw3")
        collection = db.get_collection(layer)
        
        # In production, this would be async
        cursor = collection.find().limit(limit)
        return list(cursor)


class FileStorage(StorageBackend):
    """Local file storage backend (for development/testing)."""
    
    def __init__(self, config: StorageConfig):
        self.config = config
        self.base_path = config.connection_string or "./data"
        import os
        os.makedirs(self.base_path, exist_ok=True)
    
    async def write(self, layer: str, data: List[Dict[str, Any]]):
        """Write data to file."""
        import json
        from datetime import datetime
        from pathlib import Path
        
        path = Path(self.base_path) / layer
        path.mkdir(parents=True, exist_ok=True)
        
        filename = path / f"{datetime.utcnow().isoformat()}.json"
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        
        logger.debug(f"Wrote {len(data)} records to file: {filename}")
    
    async def read(self, layer: str, limit: int = 100) -> Optional[List[Dict[str, Any]]]:
        """Read data from file."""
        import json
        from pathlib import Path
        
        path = Path(self.base_path) / layer
        if not path.exists():
            return None
        
        # Read most recent file
        files = sorted(path.glob("*.json"), reverse=True)
        if not files:
            return None
        
        with open(files[0], "r") as f:
            data = json.load(f)
        
        return data[:limit]


def get_storage_backend(backend: str, config: StorageConfig) -> StorageBackend:
    """Factory function to get storage backend."""
    backends = {
        "s3": S3Storage,
        "postgres": PostgreSQLStorage,
        "postgresql": PostgreSQLStorage,
        "mongodb": MongoDBStorage,
        "file": FileStorage,
    }
    
    backend_class = backends.get(backend.lower())
    if not backend_class:
        raise ValueError(f"Unknown storage backend: {backend}")
    
    return backend_class(config)

