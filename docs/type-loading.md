A feature of gtirb-ddisasm-retypd to take in information that already exists in the GTIRB IR pertaining to type information, and to use it as a source of information for propagating type information around. We do this by adding a step in-between type generation and type solving which replaces functions with known prototypes with constraints generated around the types of the prototype. This allows for ground truth information to be propagated. This resolves issue #2.

# Constraint generation for gtirb-types

There are two cases we want to consider for generating constraints for gtirb-types:

1. We have detailed type information, i.e. gtirb-types has the equivalent of:
   ```c
   struct A {
        int field1;
        float field2;
   };
2. We do not have detailed type information, i.e. we may have a function which takes in an opaque type such as `FILE*`, where the contents of `FILE` are unknown, but we want to propagate around that `FILE*` is the correct type.

These two cases are handled separately.

## Detailed Types

The way we generate constraints for gtirb-types is a recursive algorithm which generates path labels for inputs and pointer accesses, and then finally generates a properly ordered constraint when it reaches a terminal (i.e. lattice element) type. Ordering is dependent on whether or not the the type is generated from an input or an output. For example, if we have a prototype `void test(int* x);` we would want the constraint

```math
test.in_0.load.σ4@0 \sqsubseteq int32
```

However if we had the prototype `int* test` we would want:

```math
int32 \sqsubseteq test.out.store.σ4@0
```

In the implementation this is tracked by `RetypdGtirbReader.Step` which tracks whether the current recursion is for a left-hand side element (such as a function input) or a right-hand side element (such as a function output). At the leaf nodes it also handles ordering the two `DerivedTypeVariable` objects into a `SubtypeConstraint` which is inserted into the `ConstraintSet`.

## Opaque Types

In the case of an opaque type we assume we will never see a direct access on the opaque type, and thus aren't worried about inferring fields for it as much as we are worried about denoting which other functions/types refer to this opaque type. To this end we insert a lattice element for each opaque type, which is strictly inserted into the lattice as $`\top \rightarrow \tau \rightarrow \bot`$. The reasoning being that we never want to merge a opaque type with another lattice element. If we run into a situation where there's an ambiguity between an opaque type and another lattice element (either another opaque type or an atomic type such as int/float) then we should assume $`\bot`$ since that should be impossible.
