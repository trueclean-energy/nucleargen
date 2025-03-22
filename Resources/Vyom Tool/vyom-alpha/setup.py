from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="vyom",
    version="0.1.0",
    author="Rahul Agarwal",
    author_email="rahul@trueclean.energy",
    description="Nuclear LMP Safety Case Accelerator using PRA",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://nuclearlicensing.io/app",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "click>=8.0.0",
        "duckdb>=0.7.0",
        "jsonpath-ng>=1.5.0",
    ],
    entry_points={
        "console_scripts": [
            "vyom=vyom.cli:cli",
        ],
    },
)
