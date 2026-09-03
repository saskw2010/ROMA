from setuptools import setup


setup(
    name="security-auditor",
    version="0.1.0",
    description="Multi-agent security auditing tool",
    packages=["src"],
    install_requires=[
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": ["pytest>=8.0.0", "pytest-asyncio>=0.23.0"],
    },
    entry_points={"console_scripts": ["security-audit=src.audit:main"]},
)
