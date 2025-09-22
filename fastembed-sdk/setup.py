#!/usr/bin/env python3
"""
FastEmbed SDK Setup
High-performance embedding SDK with Snapdragon NPU acceleration
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fastembed-sdk",
    version="0.1.0",
    author="FastEmbed",
    author_email="contact@fastembed.dev",
    description="High-performance embedding SDK with Snapdragon NPU acceleration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fastembed/fastembed-sdk",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "httpx>=0.24.0",
        "pydantic>=2.0.0",
        "typing-extensions>=4.0.0",
        "numpy>=1.21.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "benchmarks": [
            "openai>=1.0.0",
            "cohere>=4.0.0",
            "matplotlib>=3.5.0",
            "pandas>=1.5.0",
            "seaborn>=0.11.0",
            "requests>=2.28.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "fastembed-benchmark=fastembed.cli:benchmark_cli",
            "fastembed-demo=fastembed.cli:demo_cli",
        ],
    },
)