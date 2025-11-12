"""
Configuration management for AZW3 pipeline.
Stack-agnostic configuration system.
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from pydantic import BaseModel, Field


class IngestionConfig(BaseModel):
    """Ingestion source configuration."""
    sources: list[Dict[str, Any]] = Field(default_factory=list)
    batch_size: int = Field(default=1000, ge=1)
    max_retries: int = Field(default=3, ge=0)


class StorageConfig(BaseModel):
    """Storage backend configuration."""
    backend: str = Field(default="s3")
    bucket: Optional[str] = None
    region: Optional[str] = None
    connection_string: Optional[str] = None


class MedallionConfig(BaseModel):
    """Medallion Architecture layer configuration."""
    bronze: Dict[str, Any] = Field(default_factory=dict)
    silver: Dict[str, Any] = Field(default_factory=dict)
    gold: Dict[str, Any] = Field(default_factory=dict)


class MLOpsConfig(BaseModel):
    """MLOps tools configuration."""
    orchestration: Optional[str] = None
    model_tracking: Optional[str] = None
    feature_store: Optional[str] = None
    compute: Optional[str] = None


class Config(BaseModel):
    """Main configuration model."""
    ingestion: IngestionConfig = Field(default_factory=IngestionConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    processing: MedallionConfig = Field(default_factory=MedallionConfig)
    mlops: MLOpsConfig = Field(default_factory=MLOpsConfig)
    
    @classmethod
    def from_file(cls, config_path: str) -> "Config":
        """Load configuration from YAML file."""
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        
        return cls(**data)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Create configuration from dictionary."""
        return cls(**data)
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        return cls(
            ingestion=IngestionConfig(
                sources=[
                    {
                        "type": os.getenv("INGESTION_TYPE", "websocket"),
                        "endpoint": os.getenv("RPC_ENDPOINT", ""),
                    }
                ]
            ),
            storage=StorageConfig(
                backend=os.getenv("STORAGE_BACKEND", "s3"),
                bucket=os.getenv("STORAGE_BUCKET"),
                region=os.getenv("STORAGE_REGION", "us-east-1"),
            ),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return self.model_dump()

