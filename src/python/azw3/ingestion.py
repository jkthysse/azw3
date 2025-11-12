"""
Data ingestion modules for multiple sources.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from .config import IngestionConfig
from .layers import BronzeLayer

logger = logging.getLogger(__name__)


class IngestionSource(ABC):
    """Base class for ingestion sources."""
    
    @abstractmethod
    async def start(self):
        """Start ingestion."""
        pass
    
    @abstractmethod
    async def stop(self):
        """Stop ingestion."""
        pass
    
    @abstractmethod
    async def ingest(self) -> List[Dict[str, Any]]:
        """Ingest data."""
        pass


class WebSocketIngestion(IngestionSource):
    """Real-time WebSocket ingestion."""
    
    def __init__(self, endpoint: str, bronze_layer: BronzeLayer):
        self.endpoint = endpoint
        self.bronze_layer = bronze_layer
        self._running = False
        self._ws = None
    
    async def start(self):
        """Start WebSocket connection."""
        try:
            import websockets
            self._ws = await websockets.connect(self.endpoint)
            self._running = True
            logger.info(f"WebSocket connected to {self.endpoint}")
            
            # Start listening
            asyncio.create_task(self._listen())
        except ImportError:
            logger.error("websockets library not installed. Install with: pip install websockets")
            raise
        except Exception as e:
            logger.error(f"Failed to connect WebSocket: {e}")
            raise
    
    async def stop(self):
        """Stop WebSocket connection."""
        self._running = False
        if self._ws:
            await self._ws.close()
        logger.info("WebSocket disconnected")
    
    async def _listen(self):
        """Listen for WebSocket messages."""
        while self._running:
            try:
                message = await self._ws.recv()
                data = await self._parse_message(message)
                await self.bronze_layer.store(data)
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                await asyncio.sleep(1)
    
    async def _parse_message(self, message: str) -> Dict[str, Any]:
        """Parse WebSocket message."""
        import json
        return json.loads(message)
    
    async def ingest(self) -> List[Dict[str, Any]]:
        """Ingest data (handled by _listen)."""
        return []


class HistoricalIngestion(IngestionSource):
    """Historical block ingestion."""
    
    def __init__(self, endpoint: str, start_block: int, bronze_layer: BronzeLayer):
        self.endpoint = endpoint
        self.start_block = start_block
        self.bronze_layer = bronze_layer
        self._current_block = start_block
        self._running = False
    
    async def start(self):
        """Start historical ingestion."""
        self._running = True
        logger.info(f"Starting historical ingestion from block {self.start_block}")
        asyncio.create_task(self._ingest_blocks())
    
    async def stop(self):
        """Stop historical ingestion."""
        self._running = False
        logger.info("Historical ingestion stopped")
    
    async def _ingest_blocks(self):
        """Ingest blocks sequentially."""
        while self._running:
            try:
                block_data = await self._fetch_block(self._current_block)
                if block_data:
                    await self.bronze_layer.store(block_data)
                    self._current_block += 1
                else:
                    # No more blocks or error
                    await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Error ingesting block {self._current_block}: {e}")
                await asyncio.sleep(1)
    
    async def _fetch_block(self, block_number: int) -> Optional[Dict[str, Any]]:
        """Fetch block data from RPC endpoint."""
        # Placeholder for RPC call
        # In production, this would use web3.py or similar
        return {
            "block_number": block_number,
            "transaction_hash": f"0x{block_number:064x}",
            "timestamp": 1234567890,
        }
    
    async def ingest(self) -> List[Dict[str, Any]]:
        """Ingest data (handled by _ingest_blocks)."""
        return []


class APIIngestion(IngestionSource):
    """Off-chain API ingestion."""
    
    def __init__(self, provider: str, bronze_layer: BronzeLayer):
        self.provider = provider
        self.bronze_layer = bronze_layer
        self._running = False
    
    async def start(self):
        """Start API ingestion."""
        self._running = True
        logger.info(f"Starting API ingestion from {self.provider}")
        asyncio.create_task(self._poll_api())
    
    async def stop(self):
        """Stop API ingestion."""
        self._running = False
        logger.info("API ingestion stopped")
    
    async def _poll_api(self):
        """Poll API for data."""
        while self._running:
            try:
                data = await self._fetch_api_data()
                if data:
                    await self.bronze_layer.store(data)
                await asyncio.sleep(60)  # Poll every minute
            except Exception as e:
                logger.error(f"API ingestion error: {e}")
                await asyncio.sleep(5)
    
    async def _fetch_api_data(self) -> Optional[Dict[str, Any]]:
        """Fetch data from API."""
        # Placeholder for API call
        # In production, this would use aiohttp or similar
        return {
            "source": "api",
            "provider": self.provider,
            "data": {},
        }
    
    async def ingest(self) -> List[Dict[str, Any]]:
        """Ingest data (handled by _poll_api)."""
        return []


class IngestionManager:
    """Manages multiple ingestion sources."""
    
    def __init__(self, config: IngestionConfig, bronze_layer: BronzeLayer):
        self.config = config
        self.bronze_layer = bronze_layer
        self.sources: List[IngestionSource] = []
        self._initialize_sources()
    
    def _initialize_sources(self):
        """Initialize ingestion sources from config."""
        for source_config in self.config.sources:
            source_type = source_config.get("type", "").lower()
            
            if source_type == "websocket":
                source = WebSocketIngestion(
                    source_config.get("endpoint", ""),
                    self.bronze_layer
                )
            elif source_type == "historical":
                source = HistoricalIngestion(
                    source_config.get("endpoint", ""),
                    source_config.get("start_block", 0),
                    self.bronze_layer
                )
            elif source_type == "api":
                source = APIIngestion(
                    source_config.get("provider", ""),
                    self.bronze_layer
                )
            else:
                logger.warning(f"Unknown source type: {source_type}")
                continue
            
            self.sources.append(source)
    
    async def start(self):
        """Start all ingestion sources."""
        logger.info(f"Starting {len(self.sources)} ingestion sources")
        for source in self.sources:
            try:
                await source.start()
            except Exception as e:
                logger.error(f"Failed to start source: {e}")
    
    async def stop(self):
        """Stop all ingestion sources."""
        logger.info("Stopping all ingestion sources")
        for source in self.sources:
            try:
                await source.stop()
            except Exception as e:
                logger.error(f"Error stopping source: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get ingestion status."""
        return {
            "sources": len(self.sources),
            "active": sum(1 for s in self.sources if hasattr(s, "_running") and s._running),
        }

