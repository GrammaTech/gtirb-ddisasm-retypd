from ddisasm_retypd.gtirb_read import RetypdGtirbReader
from gtirb_functions import Function
from gtirb_test_helpers import (
    create_test_module,
    add_text_section,
    add_code_block,
    add_function,
)
from gtirb_types import (
    AbstractType,
    FunctionType,
    FloatType,
    GtirbTypes,
    PointerType,
    IntType,
    StructType,
    VoidType,
)
from helpers import table_test
from retypd.parser import SchemaParser
from retypd.schema import DerivedTypeVariable
from typing import List, Tuple
import gtirb
import pytest
import retypd.c_types
import uuid


class TypesBuilder:
    """A quick helper utility to generate type objects"""

    def __init__(self, module: gtirb.Module):
        self.module = module
        self.functions = {
            func.get_name(): func for func in Function.build_functions(module)
        }
        self.types = GtirbTypes(module)

        prototype_aux = gtirb.AuxData({}, "mapping<UUID,UUID>")
        module.aux_data["prototypeTable"] = prototype_aux
        self.prototypes = prototype_aux.data

    def void(self) -> AbstractType:
        void = VoidType(uuid.uuid4(), self.types)
        self.types.map[void.uuid] = void
        return void

    def integer(self, size: int, signed: bool = True) -> AbstractType:
        int_type = IntType(uuid.uuid4(), self.types, signed, size)
        self.types.map[int_type.uuid] = int_type
        return int_type

    def float(self, size: int) -> AbstractType:
        float_type = FloatType(uuid.uuid4(), self.types, size)
        self.types.map[float_type.uuid] = float_type
        return float_type

    def struct(self, size: int, args: List[Tuple[int, AbstractType]]):
        struct_type = StructType(
            uuid.uuid4(),
            self.types,
            size,
            [(offset, field.uuid) for (offset, field) in args],
        )
        self.types.map[struct_type.uuid] = struct_type
        return struct_type

    def pointer(self, pointed_to: AbstractType) -> AbstractType:
        ptr_type = PointerType(uuid.uuid4(), self.types, pointed_to.uuid)
        self.types.map[ptr_type.uuid] = ptr_type
        return ptr_type

    def function(self, args: List[AbstractType], ret: AbstractType = None):
        if ret is None:
            ret = self.void()

        func = FunctionType(
            uuid.uuid4(), self.types, ret.uuid, [arg.uuid for arg in args]
        )
        self.types.map[func.uuid] = func
        return func

    def prototype(self, name: str, func: AbstractType):
        self.prototypes[self.functions[name].uuid] = func.uuid

    def save(self):
        self.types.save()
        # This shouldn't be necessary since we copy by reference, but to be
        # safe
        self.module.aux_data["prototypeTable"].data = self.prototypes


@pytest.mark.commit
def test_gtirb_type_constraints():
    """Validate that gtirb-type tables can be generated into valid
    constraints
    """
    # Create GTIRB
    _, module = create_test_module(
        gtirb.Module.FileFormat.ELF,
        gtirb.Module.ISA.X64,
    )
    _, bi = add_text_section(module, address=0x4000)

    for i in range(7):
        add_function(module, f"test{i + 1}", add_code_block(bi, b"\xCC"))

    # Create types
    type_builder = TypesBuilder(module)
    type_builder.prototype(
        "test1", type_builder.function([type_builder.integer(4)])
    )
    type_builder.prototype(
        "test2",
        type_builder.function(
            [type_builder.float(4)], type_builder.integer(4)
        ),
    )
    type_builder.prototype(
        "test3",
        type_builder.function([type_builder.pointer(type_builder.integer(4))]),
    )
    type_builder.prototype(
        "test4",
        type_builder.function(
            [
                type_builder.pointer(
                    type_builder.pointer(type_builder.integer(4))
                )
            ]
        ),
    )
    type_builder.prototype(
        "test5",
        type_builder.function(
            [],
            type_builder.pointer(
                type_builder.pointer(type_builder.integer(4))
            ),
        ),
    )
    type_builder.prototype(
        "test6",
        type_builder.function(
            [
                type_builder.pointer(
                    type_builder.struct(
                        8,
                        [
                            (0, type_builder.integer(4)),
                            (4, type_builder.float(4)),
                        ],
                    )
                )
            ]
        ),
    )
    type_builder.prototype(
        "test7", type_builder.function([type_builder.integer(4, signed=False)])
    )
    type_builder.save()

    # Generate constraints
    reader = RetypdGtirbReader(module)
    constraint_sets = reader.load_all()

    def cs_has(constraint: str, name: str):
        assert (
            SchemaParser.parse_constraint(constraint) in constraint_sets[name]
        )

    # Validate generated constraints
    cs_has("test1.in_0 ⊑ int32", "test1")
    cs_has("void ⊑ test1.out", "test1")
    cs_has("test2.in_0 ⊑ float32", "test2")
    cs_has("int32 ⊑ test2.out", "test2")
    cs_has("test3.in_0.load.σ4@0 ⊑ int32", "test3")
    cs_has("test4.in_0.load.σ8@0.load.σ4@0 ⊑ int32", "test4")
    cs_has("int32 ⊑ test5.out.store.σ8@0.store.σ4@0", "test5")
    cs_has("test6.in_0.load.σ4@0 ⊑ int32", "test6")
    cs_has("test6.in_0.load.σ4@4 ⊑ float32", "test6")
    cs_has("test7.in_0 ⊑ uint32", "test7")


def generate_propagation_test_types(module: gtirb.Module) -> GtirbTypes:
    """Generate a prototype for a method called in the test
    test_gtirb_type_propagation
    """

    builder = TypesBuilder(module)
    builder.prototype(
        "x", builder.function([], builder.pointer(builder.integer(8)))
    )

    return builder.types


@table_test(
    """
    x:
    mov RAX, 0
    ret
    """,
    gtirb.Module.ISA.X64,
    functions=["x"],
    type_constructor=generate_propagation_test_types,
    give_types=True,
)
def test_gtirb_type_propagation(result, types):
    """Validate that when an typed method is called, types are derived
    correctly
    """
    x = types[DerivedTypeVariable("x")]
    assert len(x.params) == 0
    assert isinstance(x.return_type, retypd.c_types.PointerType)
    assert isinstance(x.return_type.target_type, retypd.c_types.IntType)
