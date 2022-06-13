from pathlib import Path
from typing import Any, List, Optional, Tuple
from ddisasm_retypd import DdisasmRetypd
from gtirb_generate_python_code.generate import generate_test_setup
from gtirb_rewriting import X86Syntax
import gtirb
import gtirb_test_helpers
import io
import os
import pytest
import shutil
import subprocess
import tempfile


# Address to load byte intervals into memory at.
BASE_ADDRESS = 0x4000


def _assign_ir_addresses(ir: gtirb.IR):
    """Assign byte intervals for sections into memory
    :param ir: gtirb.IR object to assign addresses to
    """
    current_addr = BASE_ADDRESS

    for section in ir.sections:
        for bi in section.byte_intervals:
            bi.address = current_addr
            current_addr += bi.size


def assembly_to_gtirb(
    assembly_str: str, isa: gtirb.Module.ISA, functions: List[str]
) -> gtirb.IR:
    """Assemble a string and load the result into a raw GTIRB IR object
    :param assembly_str: String of assembly to be assembled
    :param isa: ISA that the assembly code is
    :param functions: List of symbols to define as functions
    :returns: Raw GTIRB IR that was generated from the assembly
    """
    output = io.StringIO()
    syntax = (
        {"x86_syntax": X86Syntax.INTEL}
        if isa in {gtirb.Module.ISA.IA32, gtirb.Module.ISA.X64}
        else {}
    )
    generate_test_setup(
        gtirb.Module.FileFormat.ELF, isa, assembly_str, output, **syntax
    )

    code = output.getvalue()
    code_locals = {}
    code_globals = {"gtirb": gtirb, **gtirb_test_helpers.__dict__}

    exec(code, code_globals, code_locals)

    ir = code_locals["ir"]
    _assign_ir_addresses(ir)

    # Delete ELF symbol table information since ddisasm can't handle symbols
    # that are present in the symbols table but not in the auxdata table.
    module = ir.modules[0]

    symInfo = module.aux_data["elfSymbolInfo"].data

    for symbol in module.symbols:
        symInfo[symbol.uuid] = (
            0,
            "FUNC" if symbol.name in functions else "NOTYPE",
            "GLOBAL",
            "DEFAULT",
            0,
        )

    del module.aux_data["elfSymbolTabIdxInfo"]

    return code_locals["ir"]


def find_ddisasm() -> Path:
    """Locate a path to ddisasm. Currently looks in PATH and an environment
        variable $DDISASM
    :returns: Path if available, otherwise an exception is thrown
    """
    path = shutil.which("ddisasm")

    if path is not None:
        return Path(path)

    if "DDISASM" in os.environ:
        return Path(os.environ["DDISASM"]).resolve()

    raise FileNotFoundError(
        "Failed to find ddisasm in PATH or DDISASM in environment"
    )


def assembly_to_ddisasm(
    assembly_str: str, isa: gtirb.Module.ISA, functions: List[str]
) -> gtirb.IR:
    """Assemble a string, and then disassemble with ddisasm
    :param assembly_str: Assembly string to assemble
    :param isa: ISA that the assembly is
    :param functions: List of symbols to define as functions
    :returns: IR output from ddisasm, with souffle relations provided
    """
    raw_ir = assembly_to_gtirb(assembly_str, isa, functions)

    with tempfile.TemporaryDirectory() as td_:
        src = Path(td_) / "raw.gtirb"
        dest = Path(td_) / "parsed.gtirb"
        raw_ir.save_protobuf(str(src))

        ddisasm_path = find_ddisasm()

        res = subprocess.run(
            [
                str(ddisasm_path),
                str(src),
                "--ir",
                str(dest),
                "--with-souffle-relations",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        if res.returncode != 0:
            err = res.stderr.decode("utf-8")
            raise ValueError(f"Failed to disassemble: {err}")

        return gtirb.IR.load_protobuf(str(dest))


class ResultObject:
    """Object for querying intermediate results of ddisasm-retypd"""

    def __init__(self, folder: Path):
        self.results = {}

        for path in folder.glob("*"):
            text = path.read_text().strip()

            self.results[path.stem] = [
                tuple(line.split("\t"))
                for line in text.split("\n")
                if line != ""
            ]

    def assertNotContains(
        self, table: str, *queries: List[Tuple[Optional[Any], ...]]
    ):
        """Assert that a table does not contain a set of queries
        :param queries: Tuples to search, where None is a wildcard match
        """
        entries = self.results[table]
        query_strs = [tuple(str(elem) for elem in query) for query in queries]

        for entry in entries:
            for query in query_strs:
                assert not all(
                    lhs == rhs
                    for lhs, rhs in zip(entry, query)
                    if rhs is not None
                ), f"Expected to not find {query}, found {entry}"

    def assertContains(self, table: str, *queries: List[Tuple[Any, ...]]):
        """Assert that a table contains a few given queries
        :param table: Table in the datalog program
        :param queries: List of tuples to check in the program
        """
        for query in queries:
            assert (
                tuple(map(str, query)) in self.results[table]
            ), f"Expected {query} in {table}"

    def printTable(self, table: str):
        """Debug print a table to stdout"""
        print(table)
        print("-" * len(table))

        for entry in self.results[table]:
            print("\t".join(entry))

    def print(self):
        """Debug print all tables loaded to stdout"""
        for key in self.results:
            self.printTable(key)
            print()


def table_test(
    assembly_str: str, isa: gtirb.Module.ISA, functions: List[str] = []
):
    """Annotation for a given function which tests ddisasm-retypd's internal
        tables
    :param assembly_str: Assembly string of the program to test
    :param isa: ISA of the program's assembly
    :param functions: List of symbols to be defined as functions
    """

    def wrapper(func):
        ir = assembly_to_ddisasm(assembly_str, isa, functions)

        with tempfile.TemporaryDirectory() as td_:
            td = Path(td_)
            DdisasmRetypd(ir, td)(td)

            return pytest.mark.parametrize("result", [ResultObject(td)])(func)

    return wrapper
