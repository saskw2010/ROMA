from __future__ import annotations

import re
from pathlib import Path

from setuptools import find_packages, setup


PROJECT_ROOT = Path(__file__).parent
INIT_FILE = PROJECT_ROOT / "src" / "__init__.py"
README_FILE = PROJECT_ROOT / "README.md"

version_match = re.search(r'__version__\s*=\s*"([^"]+)"', INIT_FILE.read_text(encoding="utf-8"))
if not version_match:
    raise RuntimeError("Unable to determine package version.")

setup(
    name="security-auditor",
    version=version_match.group(1),
    description="Phase 1 security auditor for the ROMA project",
    long_description=README_FILE.read_text(encoding="utf-8") if README_FILE.exists() else "Security auditor",
    long_description_content_type="text/markdown",
    author="saskw2010",
    packages=find_packages(include=["src", "src.*"]),
    include_package_data=True,
    install_requires=["pydantic>=2,<3"],
    extras_require={
        "dev": [
            "build>=1.2.0",
            "pytest>=8.0.0",
            "pytest-asyncio>=0.23.0",
            "pytest-cov>=5.0.0",
            "ruff>=0.5.0",
        ]
    },
    entry_points={"console_scripts": ["security-auditor=src.audit:cli"]},
    python_requires=">=3.10",
)
