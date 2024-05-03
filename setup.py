import pathlib
from setuptools import setup, find_packages


# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="aiidalab-qe-pp",
    version="0.0.1",
    description="AiiDAlab quantum ESPRESSO app plugin for PP code",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/AndresOrtegaGuerrero/aiidalab-qe-pp",
    author="Andres Ortega-Guerrero",
    author_email="oandresg15@gmail.com",
    license="MIT License",
    classifiers=[],
    packages=find_packages(),
    install_requires=[
        "weas-widget",
    ],
    entry_points={
        "aiidalab_qe.properties": [
            "pp = aiidalab_qe_pp:pp",
        ],
        "aiida.workflows": [
            "pp_app.pp = aiidalab_qe_pp.ppworkchain:PPWorkChain",
        ],
    },
    package_data={},
    python_requires=">=3.9",
    #test_suite="setup.test_suite",
)