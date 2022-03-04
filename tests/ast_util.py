from typing import Tuple
from retypd.c_types import (
    CType,
    CharType,
    IntType,
    FunctionType,
    PointerType,
    StructType,
    Field,
    VoidType,
)
from retypd.parser import SchemaParser
from retypd.schema import ConstraintSet
from pathlib import Path
import asts
import logging
import re


class TestHeader:
    """A header from a test file"""

    def __init__(self, header_file: Path, pointer_size: int):
        self.header_file = header_file
        self.pointer_size = pointer_size
        self.namespace = {}
        self.constraints = {}
        self._preceding_comment = None
        self._load_ast()

    def _load_type_ast(self, type_ast: asts.AST) -> CType:
        """Load a type object from an AST
        :param type_ast: AST of the type
        :returns: CType object loaded
        """
        if isinstance(type_ast, asts.CPrimitiveType):
            cstr = type_ast.source_text
            if cstr == "int":
                return IntType(4, True)
            elif cstr == "char":
                return CharType(1)
            elif cstr == "void":
                return VoidType()
            elif cstr == "unsigned":
                return IntType(4, False)
            else:
                raise ValueError(f"Unknown primitive {cstr}")
        elif isinstance(type_ast, asts.CStructSpecifier):
            return self.namespace[type_ast.children[0].source_text]

    def _apply_pointers(
        self, type: CType, ast: asts.AST
    ) -> Tuple[CType, asts.AST]:
        """Apply pointer declarators to a type object
        :param type: Type object to apply pointers to
        :param ast: AST object that has the pointer declarators to unwrap
        :returns: CType with pointers applied, and AST object with pointer
            declarators unwrapped
        """
        while isinstance(ast, asts.CPointerDeclarator):
            type = PointerType(type, width=self.pointer_size)
            ast = ast.children[0]

        return (type, ast)

    def _load_ast(self):
        """ Load the ASTs functions and user-defined types """
        self.ast_root = asts.AST.from_string(
            self.header_file.read_text(), language=asts.ASTLanguage.C
        )

        for ast in self.ast_root.children:
            if isinstance(ast, asts.CDeclaration):
                ast_return = ast.type
                return_type = self._load_type_ast(ast_return)

                declarator = ast.declarator[0]
                return_type, declarator = self._apply_pointers(
                    return_type, declarator
                )

                name = declarator.declarator.source_text
                params = []

                for param in declarator.parameters.children:
                    type_ast = param.children[0]
                    param_decl = param.children[1]

                    param_type = self._load_type_ast(type_ast)
                    param_type, param_decl = self._apply_pointers(
                        param_type, param_decl
                    )
                    params.append(param_type)

                self.namespace[name] = FunctionType(return_type, params, name)

                if self._preceding_comment:
                    self.constraints[name] = self._preceding_comment
                    self._preceding_comment = None
            elif isinstance(ast, asts.CStructSpecifier):
                if len(ast.children) == 1:
                    name = ast.children[0].source_text
                    self.namespace[name] = StructType([], name=name)
                    continue

                name = ast.children[0].source_text
                fields = []

                for field in ast.children[1].children:
                    field_type = self._load_type_ast(field.type)
                    field_decl = field.children[1]
                    field_type, field_decl = self._apply_pointers(
                        field_type, field_decl
                    )
                    field_name = field_decl.source_text
                    offset = (
                        fields[-1].offset + fields[-1].ctype.size
                        if len(fields) > 0
                        else 0
                    )
                    align = self.pointer_size // 8

                    padding = (align - (offset % align)) % align
                    offset = offset + padding

                    fields.append(Field(field_type, offset, name=field_name))

                if name in self.namespace:
                    self.namespace[name].set_fields(fields)
                else:
                    self.namespace[name] = StructType(fields, name)
            elif isinstance(ast, asts.CommentAST):
                comment = ast.source_text
                try:
                    constraints = [
                        SchemaParser.parse_constraint(comment_line)
                        for comment_line in re.findall(r"\!\s*(.*)", comment)
                    ]

                    if len(constraints) > 0:
                        self._preceding_comment = ConstraintSet(constraints)
                except ValueError as e:
                    logging.warning(f"Failed to parse constraint: {e}")
            elif isinstance(ast, (asts.CEmptyStatement)):
                continue
            else:
                logging.warning(f"Failed unknown {ast}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Test helper for TestHeader, prints translated types"
    )
    parser.add_argument("file", type=Path, help="Header file to parse")
    parser.add_argument(
        "-p",
        "--pointer-size",
        type=int,
        help="Pointer size to use for pointers",
        required=True,
    )
    args = parser.parse_args()

    hf = TestHeader(args.file, args.pointer_size)

    for val in hf.namespace.values():
        print(val.pretty_print(val.name))

        if val.name in hf.constraints:
            print(hf.constraints[val.name])
