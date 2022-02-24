from setuptools import find_packages, setup
from imp import load_source

pkginfo = load_source("pkginfo.version", "src/ddisasm_retypd/version.py")
__version__ = pkginfo.__version__

setup(
    name="gtirb-ddisasm-retypd",
    version=__version__,
    description="Generate retypd types from a ddisasm-generated GTIRB file",
    author="GrammaTech, Inc.",
    install_requires=["gtirb", "gtirb-functions", "gtirb-types", "retypd"],
    extras_require={"test": ["asts", "pkginfo", "pytest", "pytest-cov"]},
    packages=find_packages("src"),
    package_dir={"": "src"},
    package_data={"": ["datalog/*.dl"]},
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "gtirb-ddisasm-retypd=ddisasm_retypd.ddisasm_retypd:main"
        ]
    },
)
