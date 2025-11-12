"""
Main Pipeline class for AZW3.
Orchestrates the entire data processing workflow.
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from .config import Config
from .layers import BronzeLayer, SilverLayer, GoldLayer
from .ingestion import IngestionManager
from .storage import StorageBackend, get_storage_backend

logger = logging.getLogger(__name__)


class Pipeline:
    """
    Main pipeline orchestrator.
    
    Handles the complete data flow from ingestion through
    the Medallion Architecture (Bronze → Silver → Gold).
    """
    
    def __init__(
        self,
        config: Optional[Config] = None,
        stack: str = "python",
        **kwargs
    ):
        """
        Initialize the pipeline.
        
        Args:
            config: Configuration object (optional)
            stack: Stack identifier (default: "python")
            **kwargs: Additional configuration parameters
        """
        self.stack = stack
        self.config = config or Config.from_env()
        
        # Initialize storage backend
        self.storage: StorageBackend = get_storage_backend(
            self.config.storage.backend,
            self.config.storage
        )
        
        # Initialize Medallion Architecture layers
        self.bronze = BronzeLayer(self.storage, self.config.processing.bronze)
        self.silver = SilverLayer(self.storage, self.config.processing.silver)
        self.gold = GoldLayer(self.storage, self.config.processing.gold)
        
        # Initialize ingestion manager
        self.ingestion = IngestionManager(
            self.config.ingestion,
            self.bronze
        )
        
        self._running = False
        logger.info(f"Pipeline initialized for stack: {stack}")
    
    async def start(self):
        """Start the pipeline."""
        if self._running:
            logger.warning("Pipeline is already running")
            return
        
        self._running = True
        logger.info("Starting AZW3 pipeline...")
        
        try:
            # Start ingestion
            await self.ingestion.start()
            
            # Start processing layers
            await asyncio.gather(
                self._process_bronze_to_silver(),
                self._process_silver_to_gold(),
            )
        except Exception as e:
            logger.error(f"Pipeline error: {e}", exc_info=True)
            raise
    
    def start_sync(self):
        """Start the pipeline synchronously."""
        asyncio.run(self.start())
    
    async def stop(self):
        """Stop the pipeline."""
        self._running = False
        await self.ingestion.stop()
        logger.info("Pipeline stopped")
    
    async def _process_bronze_to_silver(self):
        """Process data from Bronze to Silver layer."""
        while self._running:
            try:
                # Get raw data from Bronze
                raw_data = await self.bronze.get_next_batch()
                
                if raw_data:
                    # Transform to Silver
                    cleaned_data = await self.silver.process(raw_data)
                    
                    # Store in Silver layer
                    await self.silver.store(cleaned_data)
                    
                    logger.debug(f"Processed {len(cleaned_data)} records: Bronze → Silver")
            except Exception as e:
                logger.error(f"Error processing Bronze → Silver: {e}")
                await asyncio.sleep(1)
    
    async def _process_silver_to_gold(self):
        """Process data from Silver to Gold layer."""
        while self._running:
            try:
                # Get cleaned data from Silver
                cleaned_data = await self.silver.get_next_batch()
                
                if cleaned_data:
                    # Transform to Gold (features)
                    features = await self.gold.process(cleaned_data)
                    
                    # Store in Gold layer
                    await self.gold.store(features)
                    
                    logger.debug(f"Processed {len(features)} features: Silver → Gold")
            except Exception as e:
                logger.error(f"Error processing Silver → Gold: {e}")
                await asyncio.sleep(1)
    
    def get_status(self) -> Dict[str, Any]:
        """Get pipeline status."""
        return {
            "running": self._running,
            "stack": self.stack,
            "ingestion": self.ingestion.get_status(),
            "bronze": self.bronze.get_status(),
            "silver": self.silver.get_status(),
            "gold": self.gold.get_status(),
        }

