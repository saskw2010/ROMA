"""Setup script for security-auditor Phase 1."""

from setuptools import find_packages, setup


setup(
    name="security-auditor",
    version="0.1.0",
    description="Multi-agent security auditing toolkit",
    author="ROMA Contributors",
    packages=find_packages(include=["src"]),
    install_requires=["pydantic>=2.8.0"],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-asyncio>=0.23.0",
            "pytest-cov>=5.0.0",
            "ruff>=0.6.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "security-auditor=src.audit:main",
        ]
    },
)
