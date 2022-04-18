# gtirb-ddisasm-retypd

Utilize the [retypd](https://github.com/GrammaTech/retypd) algorithm to infer
type information for binaries lifted to [GTIRB](https://github.com/GrammaTech/gtirb)
with [ddisasm](https://github.com/GrammaTech/ddisasm). This relies on internal
souffle facts and outputs derived in ddisasm that are encoded in the AuxData
section of the GTIRB file. These facts are only saved to AuxData when ddisasm is
run with the `--with-souffle-relations` flag, for example:

```bash
$ ddisasm ./sample-binary --ir ./sample-binary.gtirb --with-souffle-relations
```

## Dependencies

`gtirb-ddisasm-retypd` requires the following dependencies:

- [ddisasm](https://github.com/GrammaTech/ddisasm) to lift files to
  GTIRB, however, this is not a runtime dependency.
- [gtirb](https://github.com/GrammaTech/gtirb)
- [gtirb-types](https://github.com/GrammaTech/gtirb-types)

## Usage

In order to use `gtirb-ddisasm-retypd`, lift a binary to GTIRB using ddisasm,
then execute `gtirb-ddisasm-retypd input.gtirb output.gtirb`, where
output.gtirb will have a copy of the input.gtirb, now with annotated types.

```
usage: gtirb-ddisasm-retypd [-h] [-d DEBUG_DIR] gtirb dest

Run retypd on ddisasm-generated GTIRB files

positional arguments:
  gtirb                 ddisasm generated GTIRB to operate on
  dest                  Path to write GTIRB to

optional arguments:
  -h, --help            show this help message and exit
  -d DEBUG_DIR, --debug-dir DEBUG_DIR
                        retypd constraint gen debug
```

## Structure

The high level dataflow of this looks like:

1. `ddisasm` generates the GTIRB of a given binary, including the generated
   souffle facts and outputs as AuxData members
2. `gtirb-ddisasm-retypd` is invoked and outputs the associated facts and
   outputs encoded in the input GTIRB file as facts files in a facts directory
   (this can be a temporary directory, or if invoked with `--debug-dir` can be
   output to a user-selected directory, this will also contain outputs from
   the ddisasm-retypd souffle program.
3. Once the output folder is generated, the ddisasm-retypd souffle program
   runs, which involves a few components:
    - **Per-architecture type sink and instruction-table information**, in
      `arch.dl`. This is for providing instructions with type-specific
      information, and for denoting things like PUSH/POP in a
      architecture-generic way.
    - **Calling-convention information**, in `callingconv.dl`. This is for
      providing information about which registers are used for which parameters
      in calling conventions, which parameters are provided on the stack.
      Eventually this will for architectures that require it, include an
      identification pass for calling convention. Right now it assumes that for
      a given loaded binary there is only one valid calling convention.
    - **Stack Analysis**, in `stack_tracker.dl`. This is currently used for
      tracking stack height information across registers, though is intended to
      be expanded in the future. This currently populates the
      `stack_pointer_tracking` table which determine at which address, which
      register, has a pointer to which stack depth. In the future we'll stack
      recording accesses to stack variables, computing live ranges of
      stack-stored values, computing stack passed arguments, and ultimately
      using that for improving parameter detection and stack variable recovery.
    - **Function Signature Analysis**, in `signature.dl`. This is where the
      strategies for inferring function arguments and function returns are.
    - **Subtype generation**, in `subtype.dl`. This is where intermediate
      representation facts (such as def-use chains, function signature
      information, type-sinks etc.) are aggregated into a single representation
      such as `subtype_reg`, `subtype_mem`, etc.
    - **Constraint generation**, in `retypd.dl`. This is where subtypes
      generated in `subtype.dl` are formatted as retypd-parsable constraints.
4. Once constraints are output by `retypd.dl`, these are then parsed by retypd
   into per-function `ConstraintSet` objects, and solved into a map from
   DerivedTypeVariable -> Sketch. These are then passed to the `CTypeGenerator`
   from retypd to generate `CType` objects.
5. `CType` objects are then translated to `gtirb-type` objects in `gtirb.py`,
   which are saved to the final output GTIRB file.

## Known limitations

- Currently there's a limited number of per-architecture type-revealing
  instructions listed, and otherwise the ddisasm `arch.arithmetic_operation`
  and `arch.logic_operation` are used, which aren't intended to be used for
  these. This leads to some inaccuracies. This also doesn't include information
  such as floating point operations and vectorized operations.
- Currently any instruction thats `OPC Reg, Num`, such add `Mul EAX, 2` is
  type-sunk as `int <= Reg`. This doesn't work for things like `SHR RAX, 4`
  which need to be type-sunk as `uint`. This should in general be done with the
  per-opcode type-sinking.
- Currently any access to an input parameter will generate a
  `FUNC.in_N <= Reg`. It seems like retypd constraints aren't huge fans of
  this:
    ```
    test_recursive.in_0 ⊑ X
    void ⊑ test_recursive.out
    test_recursive.in_0 ⊑ Y
    int ⊑ X.store.σ4@0
    Y ⊑ Y.store.σ8@8
    ```
  generates:

    ```c
    struct struct_0 {
        int32_t field_0; // offset 0
        struct struct_1* field_1; // offset 8
    };
    struct struct_1 {
        uint8_t field_0[8]; // offset 8
    };
    ```

  while,

    ```
    test_recursive.in_0 ⊑ X
    void ⊑ test_recursive.out
    int ⊑ X.store.σ4@0
    X ⊑ X.store.σ8@8
    ```

  generates:

    ```c
    struct struct_0 {
        int32_t field_0; // offset 0
        struct struct_1* field_1; // offset 8
    };
    struct struct_1 {
        uint8_t field_0[4]; // offset 0
        uint8_t field_1[8]; // offset 8
    };
    ```
 - Currently retypd's algorithm will always generate the safest typing of the
   given constraint-set. This means that types will typically flow to callees
   from callers, but not vice-versa. This results in many partial types being
   created, and on a per-function level structured inputs will not be merged in
   an expected way.
 - Currently constraints are only generated for functions, and not globals. For
   per-function information, types are only generated for the inputs and
   outputs of a given function, as this is what retypd is currently labeling as
   "interesting."
 - Currently retypd is responsible for determining the FunctionType output,
   which will correspondingly determine the ultimate number of arguments that a
   function is said to have. However this may be in conflict with the arguments
   our analysis deduced, since retypd may simplify out a `.in_*` relation that
   causes fewer parameters to be present in the final output.

## Copyright and Acknowledgments

Copyright (C) 2022 GrammaTech, Inc.

This code is licensed under the GPLv3 license. See the LICENSE file in the project root for license terms.

This project is sponsored by the Office of Naval Research, One Liberty Center, 875 N. Randolph Street, Arlington, VA 22203 under contract #N68335-17-C-0700. The content of the information does not necessarily reflect the position or policy of the Government and no official endorsement should be inferred.
