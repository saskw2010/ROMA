from setuptools import setup


setup(
    name="security-auditor",
    version="0.1.0",
    description="Multi-agent security auditing tool",
    py_modules=["agents", "audit", "config", "logging", "models"],
    package_dir={"": "src"},
    install_requires=[
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": ["pytest>=8.0.0", "pytest-asyncio>=0.23.0"],
    },
    entry_points={"console_scripts": ["security-audit=audit:main"]},
)
