"""
Example using AZW3 with MLflow integration.
"""

from azw3 import Pipeline, Config
from azw3.integrations import MLflowFeatureStore

# Create configuration
config = Config.from_file("config.yaml")

# Initialize pipeline
pipeline = Pipeline(config=config, stack="python")

# Initialize MLflow feature store
mlflow_store = MLflowFeatureStore(experiment_name="web3-ml-experiment")

# Start pipeline
pipeline.start_sync()

# Log features to MLflow
features = {
    "gas_price_avg": 45.2,
    "transaction_volume": 1000000,
    "user_activity_score": 0.75
}

mlflow_store.log_features(features)

