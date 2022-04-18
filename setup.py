# Copyright (C) 2022 GrammaTech, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# This project is sponsored by the Office of Naval Research, One
# Liberty Center, 875 N. Randolph Street, Arlington, VA 22203 under
# contract #N68335-17-C-0700.  The content of the information does not
# necessarily reflect the position or policy of the Government and no
# official endorsement should be inferred.

from setuptools import find_packages, setup
from imp import load_source

pkginfo = load_source("pkginfo.version", "src/ddisasm_retypd/version.py")
__version__ = pkginfo.__version__

setup(
    name="gtirb-ddisasm-retypd",
    version=__version__,
    description="Generate retypd types from a ddisasm-generated GTIRB file",
    author="GrammaTech, Inc.",
    install_requires=[
        "gtirb",
        "gtirb-capstone",
        "gtirb-functions",
        "gtirb-types",
        "retypd",
    ],
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
