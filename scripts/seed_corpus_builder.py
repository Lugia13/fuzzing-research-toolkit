#!/usr/bin/env python3
"""
seed_corpus_builder.py

Takes a small handful of example input files and expands them into a
larger, more structurally diverse seed corpus using targeted, deliberate
mutations, rather than starting a fuzzing run from two or three files
and hoping the fuzzer's own mutation engine finds the format's structure
entirely on its own.

This is not a fuzzer. It doesn't run the target and doesn't check for
crashes. It only produces candidate seeds; run them through your actual
fuzzer's corpus minimizer afterward (see corpus_minimize.sh) to keep only
the ones that add real coverage.

Mutations applied to each input:
  - truncation at several points (tests how the parser handles cut off input)
  - duplication of the whole input (tests handling of back to back records)
  - byte at every power of two offset flipped, one mutation per offset
  - every run of ASCII digits replaced with a boundary value (0, 1, max)

Usage:
    python3 seed_corpus_builder.py <input_file_or_dir> <output_dir>
"""

import os
import re
import sys

DIGIT_RUN_RE = re.compile(rb"\d+")
BOUNDARY_VALUES = [b"0", b"1", b"999999999"]


def truncations(data):
    points = sorted({len(data) // 4, len(data) // 2, (len(data) * 3) // 4})
    return [data[:p] for p in points if 0 < p < len(data)]


def duplication(data):
    return [data + data]


def bit_flips_at_power_of_two_offsets(data):
    results = []
    offset = 1
    while offset < len(data):
        mutated = bytearray(data)
        mutated[offset] ^= 0xFF
        results.append(bytes(mutated))
        offset *= 2
    return results


def digit_boundary_substitutions(data):
    results = []
    matches = list(DIGIT_RUN_RE.finditer(data))
    for m in matches[:5]:  # cap how many we generate per input, per value
        for value in BOUNDARY_VALUES:
            mutated = data[:m.start()] + value + data[m.end():]
            results.append(mutated)
    return results


def expand(data):
    seeds = [data]
    seeds += truncations(data)
    seeds += duplication(data)
    seeds += bit_flips_at_power_of_two_offsets(data)
    seeds += digit_boundary_substitutions(data)
    # De-duplicate while keeping order, since several mutations can
    # legitimately collide on small inputs.
    seen = set()
    unique_seeds = []
    for s in seeds:
        if s not in seen:
            seen.add(s)
            unique_seeds.append(s)
    return unique_seeds


def collect_input_files(path):
    if os.path.isfile(path):
        return [path]
    files = []
    for root, _dirs, names in os.walk(path):
        for name in names:
            files.append(os.path.join(root, name))
    return sorted(files)


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input_file_or_dir> <output_dir>", file=sys.stderr)
        sys.exit(1)
    input_path, output_dir = sys.argv[1], sys.argv[2]
    os.makedirs(output_dir, exist_ok=True)

    input_files = collect_input_files(input_path)
    if not input_files:
        print(f"No input files found at {input_path}", file=sys.stderr)
        sys.exit(1)

    total_written = 0
    for in_path in input_files:
        with open(in_path, "rb") as f:
            data = f.read()
        base_name = os.path.basename(in_path)
        for i, seed in enumerate(expand(data)):
            out_path = os.path.join(output_dir, f"{base_name}.seed{i:03d}")
            with open(out_path, "wb") as f:
                f.write(seed)
            total_written += 1

    print(f"Expanded {len(input_files)} input file(s) into {total_written} seed(s) in {output_dir}")
    print("Run these through your fuzzer's corpus minimizer before a real "
          "campaign (see corpus_minimize.sh); not every generated seed is "
          "worth keeping.")


if __name__ == "__main__":
    main()
