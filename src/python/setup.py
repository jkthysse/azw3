"""
Setup script for AZW3 Python package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent.parent.parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="azw3",
    version="1.0.0",
    description="Web3 Data Pipeline for Model Ingestion",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="AZW3 Community",
    author_email="support@azw3.io",
    url="https://github.com/jkthysse/azw3",
    packages=find_packages(where="src/python"),
    package_dir={"": "src/python"},
    python_requires=">=3.8",
    install_requires=[
        "web3>=6.0.0",
        "pydantic>=2.0.0",
        "pyyaml>=6.0.0",
        "aiohttp>=3.9.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
    ],
    extras_require={
        "mlflow": ["mlflow>=2.8.0"],
        "feast": ["feast>=0.36.0"],
        "airflow": ["apache-airflow>=2.7.0"],
        "s3": ["boto3>=1.28.0"],
        "postgres": ["psycopg2-binary>=2.9.0"],
        "mongodb": ["pymongo>=4.6.0"],
        "all": [
            "mlflow>=2.8.0",
            "feast>=0.36.0",
            "apache-airflow>=2.7.0",
            "boto3>=1.28.0",
            "psycopg2-binary>=2.9.0",
            "pymongo>=4.6.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)

