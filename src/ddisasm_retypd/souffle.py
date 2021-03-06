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

import logging
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def _find_souffle() -> Path:
    """Find a suitable souffle binary to use
    :returns: Path to the souffle binary
    """
    which_path = shutil.which("souffle")

    if which_path is not None:
        return Path(which_path)

    raise FileNotFoundError("Failed to find souffle")


def execute_souffle(
    facts: Path,
    datalog: Path,
    output_rels: List[str],
    compiled: bool = False,
    debug_dir: Optional[Path] = None,
) -> Dict[str, List[Tuple[str, ...]]]:
    """Execute souffle and get some outputs from it
    :param facts: Path to pre-existing facts
    :param datalog: Path to datalog file to execute
    :param output_rels: List of relations to get outputs of
    :param compiled: Whether or not to generate an executable for this
    :param debug_dir: Debug output directory
    :returns: Mapping of relations to list of rows
    """
    souffle = _find_souffle()
    output = {}

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = debug_dir or Path(tmpdir)
        program_path = tmpdir_path / "prog.cpp"

        compile_flags = []
        if compiled:
            compile_flags = ["--compile", f"--generate={program_path}"]

        subprocess.call(
            [
                f"{souffle.resolve()}",
                f"--fact-dir={facts.resolve()}",
                f"--output-dir={tmpdir_path}",
                "--macro='DEBUG=1'",
                *compile_flags,
                f"{datalog.resolve()}",
            ]
        )

        for output_rel in output_rels:
            path = tmpdir_path / f"{output_rel}.csv"

            if not path.exists():
                logging.error(f"No data for {output_rel}")
                continue

            lines = path.read_text().splitlines()
            output[output_rel] = [tuple(line.split("\t")) for line in lines]

    return output
