import argparse
import re
import asts
import gtirb
import tempfile

from collections import defaultdict
from ddisasm_retypd.ddisasm_retypd import DdisasmRetypd
from pathlib import Path
from typing import Optional


def main():
    parser = argparse.ArgumentParser(
        description="Generate unit tests for the current generated tests"
    )
    parser.add_argument("workdir", type=Path, help="Location to read from")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Location to write output to",
        required=True,
    )
    args = parser.parse_args()

    source_dir = args.workdir / "src"
    gtirb_dir = args.workdir / "gtirb"
    gtirbs = list(gtirb_dir.glob("*.gtirb"))

    gtirb_headers = {
        gtirb_file: (
            source_dir / f'{gtirb_file.name.rsplit("-", maxsplit=1)[0]}.h'
        )
        for gtirb_file in gtirbs
    }

    comments = defaultdict(dict)

    for gtirb_file in gtirbs:
        opt = gtirb_file.stem.rsplit("-", maxsplit=1)[1]

        with tempfile.TemporaryDirectory() as td:
            ir = gtirb.IR.load_protobuf(str(gtirb_file))
            dr = DdisasmRetypd(ir, Path(td))
            dr._exec_souffle(dr.facts_dir, Path(td))

            constraint_map = dr._insert_subtypes()

        for dtv, derived_constraint in constraint_map.items():
            comment = "\n/**\n"
            comment += f" * Generated constraints for {dtv} at -{opt}\n"
            comment += " *\n"
            for constraint in derived_constraint.subtype:
                comment += f" * #[{opt}] {constraint}\n"
            comment += " */"
            comments[str(dtv)][opt] = comment

    def insert_decl_comments(ast: asts.AST) -> Optional[asts.LiteralOrAST]:
        if isinstance(ast, asts.RootAST):
            for child in ast.children:
                children_line = None

                for (range_child, ranges) in ast.ast_source_ranges():
                    if child == range_child:
                        children_line = min(ranges, key=lambda x: x[0])[0]
                        break
                else:
                    print(f"Failed to find source range for {child}")
                    continue

                if not isinstance(child, asts.CDeclaration):
                    continue

                name_ast = child.children[1].children[0]

                while isinstance(
                    name_ast,
                    (asts.CPointerDeclarator, asts.CFunctionDeclarator0),
                ):
                    name_ast = child.children[0]

                if isinstance(name_ast, asts.CStructSpecifier):
                    continue

                assert isinstance(name_ast, asts.CIdentifier), (
                    f"Failed to derive identifier for {name_ast}: "
                    f"{name_ast.source_text}"
                )
                name = name_ast.source_text

                if name not in comments:
                    continue

                prev_comments = {}

                for prev_child in ast.children:
                    if isinstance(prev_child, asts.CComment):
                        prev_comment = prev_child.source_text
                        prev_gen = re.findall(
                            r"Generated constraints for (.*) at -(O\d)",
                            prev_comment,
                        )

                        if len(prev_gen) > 0:
                            prev_func, prev_opt = prev_gen[0]

                            if prev_func == name:
                                prev_comments[prev_opt] = prev_child
                    elif isinstance(prev_child, asts.CEmptyStatement):
                        continue
                    else:
                        break

                opts = sorted(comments[name].items(), key=lambda x: x[0])[::-1]

                for opt, comment in opts:
                    new_ast = asts.AST.from_string(
                        comment, asts.ASTLanguage.C, deepest=True,
                    )
                    assert isinstance(new_ast, asts.CComment)

                    if opt in prev_comments:
                        replace_point = prev_comments[opt]
                        asts.AST.replace(ast, replace_point, new_ast)
                    else:
                        insert_point = ast.ast_at_point(children_line - 1, 1)

                        ast = asts.AST.insert(ast, insert_point, new_ast)

            return ast

    headers = set(gtirb_headers.values())

    for header_file in headers:
        header = asts.AST.from_string(
            header_file.read_text(), asts.ASTLanguage.C
        )

        header_new = asts.AST.transform(header, insert_decl_comments)
        (args.output / header_file.name).write_text(header_new.source_text)


if __name__ == "__main__":
    main()
