from setuptools import find_packages, setup


setup(
    name="roma-ml-training",
    version="0.1.0",
    description="ML training and recommendation utilities for ROMA",
    package_dir={"": "."},
    packages=find_packages(where="."),
    include_package_data=True,
    install_requires=["numpy>=1.26"],
)
