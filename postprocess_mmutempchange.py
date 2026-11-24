#!/usr/bin/env python3
"""Move MMU toolchange temperature changes after the cooling moves.

PrusaSlicer emits the M104 of the next filament before the cooling moves, so the
hotend heats or cools while the previous filament is still in the melt zone. This
script moves every such M104 right after the last G4 dwell that precedes the
T<n> toolchange command.

A toolchange block starts at the "; CP TOOLCHANGE UNLOAD" marker (PrusaSlicer 2.x)
or, for older G-code without the marker, at an M104 that directly follows a
retraction (G1 E-...). The block ends at the T<n> line. Blocks without a G4 after
the M104 are written unchanged.

Usage: postprocess_mmutempchange.py <file.gcode>   (the file is edited in place)
"""
import re
import sys

UNLOAD_MARKER = "; CP TOOLCHANGE UNLOAD"
TOOLCHANGE = re.compile(r"^T\d+\b")
DWELL = re.compile(r"^G4\s+[SP]")
TEMPERATURE = re.compile(r"^M104\b")
RETRACT = re.compile(r"^G1\s+E-")


def reorder_block(block):
    """Return the block with its M104 lines moved after its last G4 dwell."""
    last_dwell = max((i for i, line in enumerate(block) if DWELL.match(line)), default=-1)
    moved = [line for line in block[:last_dwell] if TEMPERATURE.match(line)]
    if not moved:
        return block
    head = [line for line in block[: last_dwell + 1] if not TEMPERATURE.match(line)]
    return head + moved + block[last_dwell + 1 :]


def process(lines):
    output = []
    block = None
    previous = ""
    for line in lines:
        if block is None:
            starts_block = line.startswith(UNLOAD_MARKER) or (
                TEMPERATURE.match(line) and RETRACT.match(previous)
            )
            if starts_block:
                block = [line]
            else:
                output.append(line)
        elif TOOLCHANGE.match(line):
            output.extend(reorder_block(block))
            output.append(line)
            block = None
        else:
            block.append(line)
        previous = line
    if block is not None:
        output.extend(block)
    return output


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    path = sys.argv[1]
    with open(path, "r") as source:
        lines = source.readlines()
    with open(path, "w") as target:
        target.writelines(process(lines))


if __name__ == "__main__":
    main()
