from setuptools import find_packages, setup


setup(
    name="security-auditor",
    version="0.1.0",
    description="Phase 1 security auditing toolkit for ROMA",
    packages=find_packages(include=["src", "security_auditor", "security_auditor.*"]),
    install_requires=["pydantic>=2.0"],
    entry_points={"console_scripts": ["security-audit=security_auditor.audit:main"]},
)
