from setuptools import setup, find_packages

setup(
    name="cased",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click",
        "requests",
        "prompt_toolkit",
    ],
    entry_points={
        "console_scripts": [
            "cased=cased.cli:cli",
        ],
    },
)
