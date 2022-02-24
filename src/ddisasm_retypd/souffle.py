import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def _find_souffle() -> Path:
    """ Find a suitable souffle binary to use
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
    """ Execute souffle and get some outputs from it
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
        compile = (
            ["--compile", f"--generate={tmpdir_path}/prog.cpp"]
            if compiled
            else []
        )

        subprocess.call(
            [
                f"{souffle.resolve()}",
                f"--fact-dir={facts.resolve()}",
                f"--output-dir={tmpdir_path}",
            ]
            + compile
            + [f"{datalog.resolve()}"]
        )

        for output_rel in output_rels:
            path = tmpdir_path / f"{output_rel}.csv"

            if not path.exists():
                raise FileNotFoundError(f"No data for {output_rel}")

            lines = path.read_text().splitlines()
            output[output_rel] = [tuple(line.split("\t")) for line in lines]

    return output
