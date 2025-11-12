"""
Airflow DAG integration.
"""

import logging
from typing import Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AirflowDAG:
    """Airflow DAG wrapper for AZW3 pipeline."""
    
    def __init__(self, pipeline, schedule_interval: str = "@hourly"):
        self.pipeline = pipeline
        self.schedule_interval = schedule_interval
        self._dag = None
    
    def _get_dag(self):
        """Get Airflow DAG (lazy initialization)."""
        if self._dag is None:
            try:
                from airflow import DAG
                from airflow.operators.python import PythonOperator
                
                default_args = {
                    "owner": "azw3",
                    "depends_on_past": False,
                    "start_date": datetime(2024, 1, 1),
                    "email_on_failure": False,
                    "email_on_retry": False,
                    "retries": 1,
                    "retry_delay": timedelta(minutes=5),
                }
                
                self._dag = DAG(
                    "azw3_pipeline",
                    default_args=default_args,
                    description="AZW3 Web3 Data Pipeline",
                    schedule_interval=self.schedule_interval,
                    catchup=False,
                )
                
                # Add pipeline task
                run_pipeline = PythonOperator(
                    task_id="run_pipeline",
                    python_callable=self.pipeline.start_sync,
                    dag=self._dag,
                )
                
            except ImportError:
                raise ImportError("apache-airflow not installed. Install with: pip install apache-airflow")
        return self._dag
    
    def get_dag(self):
        """Get the Airflow DAG object."""
        return self._get_dag()

