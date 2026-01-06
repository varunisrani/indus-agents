"""
Setup script for indus-agents CLI

This makes the CLI installable as a package with a convenient entry point.
"""

from setuptools import setup, find_packages

setup(
    name="indusagi",
    version="0.2.0",
    description="IndusAGI - Modern Agent Framework",
    author="IndusAGI Team",
    license="MIT",
    py_modules=["cli", "agent", "tools"],
    install_requires=[
        "openai>=1.12.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "typer>=0.9.0",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "indusagi=cli:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
