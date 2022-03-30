import csv
import gtirb
import logging

from gtirb_functions import Function
from pathlib import Path
from typing import Dict, Set, Tuple


def filter_name(function: Function) -> str:
    """ Do name filtering identical to the one implemented for souffle
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

    if module.isa in (
        gtirb.module.Module.ISA.X64,
        gtirb.module.Module.ISA.ARM64,
        gtirb.module.Module.ISA.MIPS64,
        gtirb.module.Module.ISA.PPC64,
    ):
        return (8, 8)
    elif module.isa == gtirb.module.Module.ISA.PPC32:
        return (4, 8)
    elif module.isa in (
        gtirb.module.Module.ISA.ARM,
        gtirb.module.Module.ISA.IA32,
        gtirb.module.Module.ISA.MIPS32,
    ):
        return (4, 4)
    else:
        raise NotImplementedError()


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


csv.register_dialect("souffle", delimiter="\t", quoting=csv.QUOTE_NONE)


def extract_block_relations(ir: gtirb.IR, directory: Path):
    """ Write souffle facts about blocks in the CFG for a GTIRB IR
    :param ir: IR that is being loaded
    :param directory: Directory to output facts to
    """
    blocks = []

    for module in ir.modules:
        if not any(module.code_blocks):
            return

        for block in module.code_blocks:
            blocks.append((block.address, block.size))

    with open(directory / "block.facts", "w") as f:
        csv.writer(f, "souffle").writerows(blocks)


def extract_edge_relations(ir: gtirb.IR, directory: Path):
    """ Write souffle facts about edges in the CFG for a GTIRB IR
    :param ir: IR that is being loaded
    :param directory: Directory to output facts to
    """
    edges = []
    top_edges = []
    symbol_edges = []

    for edge in ir.cfg:
        if isinstance(edge.source, gtirb.CodeBlock):
            conditional = str(edge.label.conditional).lower()
            indirect = str(not edge.label.direct).lower()
            label_type = edge.label.type.name.lower()

            if isinstance(edge.target, gtirb.CodeBlock):
                edges.append(
                    (
                        edge.source.address,
                        edge.target.address,
                        conditional,
                        indirect,
                        label_type,
                    )
                )
            elif isinstance(edge.target, gtirb.ProxyBlock):
                if any(edge.target.references):
                    symbol = next(edge.target.references)

                    symbol_edges.append(
                        (
                            edge.source.address,
                            symbol.name,
                            conditional,
                            indirect,
                            label_type,
                        )
                    )
                else:
                    top_edges.append(
                        (
                            edge.source.address,
                            conditional,
                            indirect,
                            label_type,
                        )
                    )

    with open(directory / "cfg_edge.facts", "w") as f:
        csv.writer(f, "souffle").writerows(edges)

    with open(directory / "cfg_edge_to_top.facts", "w") as f:
        csv.writer(f, "souffle").writerows(top_edges)

    with open(directory / "cfg_edge_to_symbol.facts", "w") as f:
        csv.writer(f, "souffle").writerows(symbol_edges)


def extract_cfg_relations(ir: gtirb.IR, directory: Path):
    """ Write souffle facts from the CFG in the current GTIRB IR
    :param ir: IR that is being loaded
    :param directory: Directory to output facts to
    """
    extract_block_relations(ir, directory)
    extract_edge_relations(ir, directory)


def extract_arch_relations(ir: gtirb.IR, directory: Path):
    """ Write souffle facts from the architecture in the current GTIRB IR
    :param ir: IR that is being loaded
    :param directory: Directory to output facts to
    """
    pointer, _ = get_arch_sizes(ir)
    (directory / "arch.pointer_size.facts").write_text(str(pointer))
