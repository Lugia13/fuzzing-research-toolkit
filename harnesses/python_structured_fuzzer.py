#!/usr/bin/env python3
"""
python_structured_fuzzer.py

A grammar aware generator for a simple nested text format, built as a
working example of the approach described in
methodology/04-coverage-guided-vs-blackbox.md: generate inputs that are
valid by construction, instead of mutating bytes and hoping enough of
them happen to pass structural validation.

The example format here is a small key value block language:

    block {
      key: value
      nested {
        key2: value2
      }
    }

This is a stand in for whatever real nested, delimited format you're
actually targeting. Adapt GRAMMAR and the generate_* functions to match
the real target's structure; the generation and mutation strategy below
stays the same regardless of the specific grammar.

Usage:
    python3 python_structured_fuzzer.py <count> <output_dir>
"""

import os
import random
import string
import sys

MAX_NESTING_DEPTH = 4
MAX_KEYS_PER_BLOCK = 4


def random_identifier(rng):
    length = rng.randint(1, 8)
    return "".join(rng.choice(string.ascii_lowercase) for _ in range(length))


def random_value(rng):
    choices = [
        lambda: str(rng.randint(-(2**31), 2**31 - 1)),
        lambda: random_identifier(rng),
        lambda: '"' + "".join(rng.choice(string.printable[:95]) for _ in range(rng.randint(0, 20))) + '"',
        lambda: "",  # empty value, a common edge case real parsers mishandle
    ]
    return rng.choice(choices)()


def generate_block(rng, depth):
    lines = []
    name = random_identifier(rng)
    lines.append(f"{name} {{")

    num_keys = rng.randint(0, MAX_KEYS_PER_BLOCK)
    for _ in range(num_keys):
        key = random_identifier(rng)
        value = random_value(rng)
        lines.append(f"  {key}: {value}")

    if depth < MAX_NESTING_DEPTH and rng.random() < 0.6:
        nested = generate_block(rng, depth + 1)
        lines.append(indent(nested))

    lines.append("}")
    return "\n".join(lines)


def indent(text, spaces=2):
    pad = " " * spaces
    return "\n".join(pad + line for line in text.splitlines())


def structural_mutation(text, rng):
    """
    Apply a single structural mutation that a byte level fuzzer would
    rarely stumble into by chance: drop a closing brace, duplicate a
    block, or unbalance a quoted string. These specifically target the
    kind of parser logic that's easy to get wrong (depth tracking,
    brace matching, quote state) and hard to reach through random byte
    mutation once a format has any structural validation at all.
    """
    mutations = [
        lambda t: t.replace("}", "", 1),               # drop first closing brace
        lambda t: t + t[: len(t) // 2],                 # duplicate a prefix
        lambda t: t.replace('"', "", 1),                 # unbalance a quote
        lambda t: t.replace("{", "{" * 2, 1),            # double an opening brace
        lambda t: t[: len(t) // 2],                      # truncate mid structure
    ]
    return rng.choice(mutations)(text)


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <count> <output_dir>", file=sys.stderr)
        sys.exit(1)
    count = int(sys.argv[1])
    output_dir = sys.argv[2]
    os.makedirs(output_dir, exist_ok=True)

    rng = random.Random()
    written = 0
    for i in range(count):
        valid_input = generate_block(rng, depth=0)

        # Roughly a third of generated inputs get a structural mutation
        # applied afterward, so the corpus includes both well formed
        # inputs (to reach deep logic) and deliberately broken ones
        # (to exercise the parser's error handling paths).
        if rng.random() < 0.33:
            text = structural_mutation(valid_input, rng)
        else:
            text = valid_input

        out_path = os.path.join(output_dir, f"gen_{i:05d}.block")
        with open(out_path, "w") as f:
            f.write(text)
        written += 1

    print(f"Wrote {written} generated input(s) to {output_dir}")


if __name__ == "__main__":
    main()
