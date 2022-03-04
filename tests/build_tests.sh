#!/bin/bash
set -euo pipefail

DDISASM_BIN="${DDISASM:-ddisasm}"

SRCDIR=$(pwd)/tests/src/
BINDIR=$(pwd)/tests/binaries/
GTIRBDIR=$(pwd)/tests/gtirb/

SOURCES=$(find $SRCDIR -name "*.c")

for SOURCE in $SRCDIR/*.c;
do
    BINARY=$(basename $SOURCE .c)

    for LEVEL in 1 2 3
    do
        echo "Building $BINARY at -O$LEVEL"
        LVLBIN="$BINDIR/$BINARY-O$LEVEL"
        GTIRB="$GTIRBDIR/$BINARY-O$LEVEL.gtirb"
        gcc $SOURCE -O$LEVEL -o $LVLBIN
        $DDISASM_BIN $LVLBIN --ir $GTIRB --with-souffle-relations
    done
done
