from setuptools import setup, find_packages

setup(
    name="data-simulator",
    version="0.0.1",
    packages=find_packages(),
    description="Data simulator",
    install_requires=[
        "requests>=2.18.0<3.0.0",
        "setuptools==36.6.0",
        "rstr==2.2.6",
        "dictionaryutils~=3.0.2",
        "gen3dictionary~=2.0.1",
    ],
    dependency_links=[
        "git+https://github.com/uc-cdis/cdislogging.git@1.0.0#egg=cdislogging",
    ],
    scripts=["bin/data-simulator"],
)
