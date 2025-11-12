"""
Command-line interface for AZW3 pipeline.
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path
from .pipeline import Pipeline
from .config import Config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AZW3: Web3 Data Pipeline for Model Ingestion"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "--stack",
        type=str,
        default="python",
        help="Stack identifier (default: python)"
    )
    
    parser.add_argument(
        "--rpc-endpoint",
        type=str,
        help="RPC endpoint URL"
    )
    
    parser.add_argument(
        "--storage-backend",
        type=str,
        help="Storage backend (s3, postgres, mongodb, file)"
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config_path = Path(args.config)
    if config_path.exists():
        config = Config.from_file(str(config_path))
        logger.info(f"Loaded configuration from {config_path}")
    else:
        config = Config.from_env()
        logger.info("Using environment configuration")
    
    # Override with CLI arguments
    if args.rpc_endpoint:
        config.ingestion.sources[0]["endpoint"] = args.rpc_endpoint
    
    if args.storage_backend:
        config.storage.backend = args.storage_backend
    
    # Initialize and start pipeline
    try:
        pipeline = Pipeline(config=config, stack=args.stack)
        logger.info("Starting AZW3 pipeline...")
        pipeline.start_sync()
    except KeyboardInterrupt:
        logger.info("Pipeline stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Pipeline error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

