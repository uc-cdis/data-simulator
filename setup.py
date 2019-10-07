from setuptools import setup, find_packages

setup(
    name="data-simulator",
    version="0.0.1",
    packages=find_packages(),
    description="Data simulator",
    install_requires=["requests>=2.18.0<3.0.0", "setuptools==36.6.0", "rstr==2.2.6", "openpyxl==2.6.4"],
    dependency_links=[
        "git+https://github.com/uc-cdis/cdislogging.git@0.0.2#egg=cdislogging",
        "git+https://github.com/uc-cdis/gdcdatamodel.git@2.0.2#egg=gen3datamodel",
    ],
    scripts=["bin/data-simulator"],
)
