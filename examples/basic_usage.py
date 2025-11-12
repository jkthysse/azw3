"""
Basic usage example for AZW3 pipeline.
"""

import asyncio
from azw3 import Pipeline, Config

async def main():
    # Create configuration
    config = Config.from_dict({
        "ingestion": {
            "sources": [
                {
                    "type": "websocket",
                    "endpoint": "wss://eth-mainnet.g.alchemy.com/v2/YOUR_KEY"
                }
            ]
        },
        "storage": {
            "backend": "file",
            "connection_string": "./data"
        }
    })
    
    # Initialize pipeline
    pipeline = Pipeline(config=config, stack="python")
    
    # Start pipeline
    print("Starting AZW3 pipeline...")
    await pipeline.start()
    
    # Run for a bit
    await asyncio.sleep(60)
    
    # Check status
    status = pipeline.get_status()
    print(f"Pipeline status: {status}")
    
    # Stop pipeline
    await pipeline.stop()
    print("Pipeline stopped")

if __name__ == "__main__":
    asyncio.run(main())

