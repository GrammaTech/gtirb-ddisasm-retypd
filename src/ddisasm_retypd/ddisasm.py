import gtirb
import logging

from gtirb_functions import Function
from pathlib import Path
from typing import Dict, Set, Tuple


def filter_name(function: Function) -> str:
    """ Do name filtering similar to that which is implemented for souffle
    :param function: Function to get the filtered name of
    :returns: String of filtered name
    """
    name = function.get_name()

    if "@" in name or "." in name:
        entries = list(function.get_entry_blocks())
        return f"FUN_{entries[0].address}"
    else:
        return name


def get_callgraph(ir: gtirb.IR) -> Dict[str, Set[str]]:
    """ Get the callgraph of the GTIRB IR
    :param ir: GTIRB IR to get call graph of
    :returns: Map of call graphs
    """
    m = ir.modules[0]

    block_to_func = {}
    callgraph = {}

    for function in Function.build_functions(m):
        callgraph[filter_name(function)] = set()

        for block in function.get_all_blocks():
            block_to_func[block] = function

    for edge in ir.cfg:
        if edge.label.type == gtirb.Edge.Type.Call:
            if not isinstance(
                edge.source, gtirb.ProxyBlock
            ) and not isinstance(edge.target, gtirb.ProxyBlock):
                caller_func = block_to_func[edge.source]
                callee_func = block_to_func[edge.target]
                caller_name = filter_name(caller_func)
                callee_name = filter_name(callee_func)
                callgraph[caller_name].add(callee_name)

    return callgraph


def get_arch_sizes(ir: gtirb.IR) -> Tuple[int, int]:
    """ Address and register sizes for a given IR's ISA
    :param ir: GTIRB IR to read from, only uses module 0 for now
    :returns: (ptr, reg) sizes in bits
    """
    module = ir.modules[0]

    if module.isa == gtirb.module.Module.ISA.X64:
        return (8, 8)
    elif module.isa == gtirb.module.Module.ISA.PPC32:
        return (4, 8)

    return (4, 4)


def extract_souffle_relations(ir: gtirb.IR, directory: Path):
    """ Write souffle facts and outputs to a directory as facts
    :param ir: gtirb.IR to read souffle facts from
    :param directory: Directory to write souffle facts to
    """
    module = ir.modules[0]
    facts = module.aux_data["souffleFacts"].data
    outputs = module.aux_data["souffleOutputs"].data

    for (name, data) in facts.items():
        header, text = data
        logging.debug(f"Writing {name} of {header}")
        (directory / f"{name}.facts").write_text(text)
    for (name, data) in outputs.items():
        header, text = data
        logging.debug(f"Writing {name} of {header}")
        (directory / f"{name}.facts").write_text(text)
