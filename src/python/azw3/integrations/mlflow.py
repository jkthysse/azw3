"""
MLflow integration for feature tracking.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class MLflowFeatureStore:
    """MLflow feature store integration."""
    
    def __init__(self, experiment_name: str = "azw3-features"):
        self.experiment_name = experiment_name
        self._client = None
    
    def _get_client(self):
        """Get MLflow client (lazy initialization)."""
        if self._client is None:
            try:
                import mlflow
                mlflow.set_experiment(self.experiment_name)
                self._client = mlflow
            except ImportError:
                raise ImportError("mlflow not installed. Install with: pip install mlflow")
        return self._client
    
    def log_features(self, features: Dict[str, Any], run_id: Optional[str] = None):
        """Log features to MLflow."""
        mlflow = self._get_client()
        
        with mlflow.start_run(run_id=run_id):
            for key, value in features.items():
                if isinstance(value, (int, float)):
                    mlflow.log_metric(key, value)
                else:
                    mlflow.log_param(key, str(value))
        
        logger.debug(f"Logged {len(features)} features to MLflow")

