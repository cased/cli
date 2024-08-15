from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cased",
    version="0.1.0",
    author="Cased",
    author_email="cli@cased.com",
    description="A CLI tool for managing deployments and branches",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cased/csd",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click",
        "requests",
        "rich",
        "questionary",
        "python-dateutil",
    ],
    entry_points={
        "console_scripts": [
            "cased=cased.cli:cli",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
