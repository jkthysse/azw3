"""
AZW3: Web3 Data Pipeline for Model Ingestion

A stack-agnostic, plug-and-play pipeline for transforming blockchain data
into ML-ready features using the Medallion Architecture.
"""

__version__ = "1.0.0"
__author__ = "AZW3 Community"

from .pipeline import Pipeline
from .config import Config
from .layers import BronzeLayer, SilverLayer, GoldLayer
from .ingestion import WebSocketIngestion, HistoricalIngestion, APIIngestion

__all__ = [
    "Pipeline",
    "Config",
    "BronzeLayer",
    "SilverLayer",
    "GoldLayer",
    "WebSocketIngestion",
    "HistoricalIngestion",
    "APIIngestion",
]

