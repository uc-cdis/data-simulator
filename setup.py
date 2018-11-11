from setuptools import setup, find_packages

setup(
    name="data-simulator",
    version="0.1",
    packages=find_packages(),
    description="Data simulator",
    install_requires=[
        "dictionaryutils==2.0.0",
        "jsonschema==2.5.1",
        "PyYAML==3.11",
        "setuptools==30.1.0",
        "simplejson==3.8.1",
        "rstr==2.2.6",
    ],
)
