"""
Medallion Architecture layers: Bronze, Silver, Gold.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from .storage import StorageBackend

logger = logging.getLogger(__name__)


class BronzeLayer:
    """
    Bronze Layer: Raw Ingestion
    
    Stores raw, unprocessed blockchain data.
    Immutable, uncleaned, schema-on-read.
    """
    
    def __init__(self, storage: StorageBackend, config: Dict[str, Any]):
        self.storage = storage
        self.config = config
        self.retention_days = config.get("retention_days", 365)
        self._buffer: List[Dict[str, Any]] = []
        self._buffer_size = 1000
    
    async def store(self, data: Dict[str, Any]):
        """Store raw data in Bronze layer."""
        # Add metadata
        data["_bronze_metadata"] = {
            "ingested_at": datetime.utcnow().isoformat(),
            "layer": "bronze",
            "retention_days": self.retention_days,
        }
        
        self._buffer.append(data)
        
        # Flush buffer when full
        if len(self._buffer) >= self._buffer_size:
            await self._flush()
    
    async def _flush(self):
        """Flush buffer to storage."""
        if not self._buffer:
            return
        
        await self.storage.write("bronze", self._buffer)
        logger.debug(f"Flushed {len(self._buffer)} records to Bronze layer")
        self._buffer.clear()
    
    async def get_next_batch(self, limit: int = 100) -> Optional[List[Dict[str, Any]]]:
        """Get next batch of raw data for processing."""
        return await self.storage.read("bronze", limit=limit)
    
    def get_status(self) -> Dict[str, Any]:
        """Get layer status."""
        return {
            "layer": "bronze",
            "buffer_size": len(self._buffer),
            "retention_days": self.retention_days,
        }


class SilverLayer:
    """
    Silver Layer: Cleaned & Normalized
    
    Processes raw data from Bronze:
    - Decodes smart contract ABIs
    - Filters and validates transactions
    - Structures into validated tables
    """
    
    def __init__(self, storage: StorageBackend, config: Dict[str, Any]):
        self.storage = storage
        self.config = config
        self.validation_mode = config.get("validation", "strict")
        self._buffer: List[Dict[str, Any]] = []
        self._buffer_size = 1000
    
    async def process(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process raw data from Bronze layer."""
        cleaned_data = []
        
        for record in raw_data:
            try:
                # Decode transaction data
                decoded = await self._decode_transaction(record)
                
                # Validate
                if self._validate(decoded):
                    # Normalize structure
                    normalized = self._normalize(decoded)
                    cleaned_data.append(normalized)
            except Exception as e:
                logger.warning(f"Failed to process record: {e}")
                if self.validation_mode == "strict":
                    raise
        
        return cleaned_data
    
    async def _decode_transaction(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Decode transaction using ABI if available."""
        # Placeholder for ABI decoding logic
        # In production, this would use web3.py or similar
        return record
    
    def _validate(self, data: Dict[str, Any]) -> bool:
        """Validate cleaned data."""
        # Basic validation
        required_fields = ["block_number", "transaction_hash", "timestamp"]
        return all(field in data for field in required_fields)
    
    def _normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize data structure."""
        normalized = {
            "block_number": data.get("block_number"),
            "transaction_hash": data.get("transaction_hash"),
            "timestamp": data.get("timestamp"),
            "from_address": data.get("from"),
            "to_address": data.get("to"),
            "value": data.get("value"),
            "gas_used": data.get("gas_used"),
            "gas_price": data.get("gas_price"),
            "_silver_metadata": {
                "processed_at": datetime.utcnow().isoformat(),
                "layer": "silver",
                "validation_mode": self.validation_mode,
            }
        }
        return normalized
    
    async def store(self, data: List[Dict[str, Any]]):
        """Store cleaned data in Silver layer."""
        self._buffer.extend(data)
        
        if len(self._buffer) >= self._buffer_size:
            await self._flush()
    
    async def _flush(self):
        """Flush buffer to storage."""
        if not self._buffer:
            return
        
        await self.storage.write("silver", self._buffer)
        logger.debug(f"Flushed {len(self._buffer)} records to Silver layer")
        self._buffer.clear()
    
    async def get_next_batch(self, limit: int = 100) -> Optional[List[Dict[str, Any]]]:
        """Get next batch of cleaned data for processing."""
        return await self.storage.read("silver", limit=limit)
    
    def get_status(self) -> Dict[str, Any]:
        """Get layer status."""
        return {
            "layer": "silver",
            "buffer_size": len(self._buffer),
            "validation_mode": self.validation_mode,
        }


class GoldLayer:
    """
    Gold Layer: Feature Store Ready
    
    Aggregates Silver data into ML-ready features:
    - Time-series features
    - Behavioral features
    - Financial features
    """
    
    def __init__(self, storage: StorageBackend, config: Dict[str, Any]):
        self.storage = storage
        self.config = config
        self.feature_store = config.get("feature_store", "feast")
        self._buffer: List[Dict[str, Any]] = []
        self._buffer_size = 1000
    
    async def process(self, cleaned_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process cleaned data into ML features."""
        features = []
        
        for record in cleaned_data:
            # Extract temporal features
            temporal_features = self._extract_temporal_features(record)
            
            # Extract financial features
            financial_features = self._extract_financial_features(record)
            
            # Extract behavioral features
            behavioral_features = await self._extract_behavioral_features(record)
            
            # Combine all features
            feature_record = {
                **temporal_features,
                **financial_features,
                **behavioral_features,
                "_gold_metadata": {
                    "processed_at": datetime.utcnow().isoformat(),
                    "layer": "gold",
                    "feature_store": self.feature_store,
                }
            }
            
            features.append(feature_record)
        
        return features
    
    def _extract_temporal_features(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Extract time-series features."""
        timestamp = record.get("timestamp")
        return {
            "hour_of_day": datetime.fromtimestamp(timestamp).hour if timestamp else None,
            "day_of_week": datetime.fromtimestamp(timestamp).weekday() if timestamp else None,
            "gas_price_avg": record.get("gas_price", 0),
        }
    
    def _extract_financial_features(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Extract financial features."""
        return {
            "transaction_value": float(record.get("value", 0)),
            "gas_cost": float(record.get("gas_used", 0)) * float(record.get("gas_price", 0)),
        }
    
    async def _extract_behavioral_features(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Extract behavioral features."""
        # Placeholder for behavioral feature extraction
        # In production, this would aggregate user activity patterns
        return {
            "user_activity_score": 0.5,  # Placeholder
        }
    
    async def store(self, features: List[Dict[str, Any]]):
        """Store features in Gold layer."""
        self._buffer.extend(features)
        
        if len(self._buffer) >= self._buffer_size:
            await self._flush()
    
    async def _flush(self):
        """Flush buffer to storage."""
        if not self._buffer:
            return
        
        await self.storage.write("gold", self._buffer)
        logger.debug(f"Flushed {len(self._buffer)} features to Gold layer")
        self._buffer.clear()
    
    def get_status(self) -> Dict[str, Any]:
        """Get layer status."""
        return {
            "layer": "gold",
            "buffer_size": len(self._buffer),
            "feature_store": self.feature_store,
        }

