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
        # "dictionaryutils~=3.0.2",
        "dictionaryutils",
        # "gen3dictionary~=2.0.1",
        "gen3dictionary",
    ],
    dependency_links=[
        "git+https://github.com/uc-cdis/cdislogging.git@1.0.0#egg=cdislogging",
        # for testing purpose
        "git+https://github.com/uc-cdis/dictionaryutils.git@feat/format_upgrade#egg=dictionaryutils",
        "git+https://github.com/uc-cdis/datadictionary.git@feat/format_upgrade#egg=gen3dictionary",
    ],
    scripts=["bin/data-simulator"],
)
