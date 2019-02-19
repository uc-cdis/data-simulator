from setuptools import setup, find_packages

setup(
    name="data-simulator",
    version="0.0.4",
    packages=find_packages(),
    description="Data simulator",
    install_requires=[
        "requests>=2.18.0<3.0.0",
        "rstr>=2.2.6",
        "dictionaryutils>=2.0.3",
        "cdislogging>=0.0.2",
    ],
    scripts=["bin/data-simulator"],
)
