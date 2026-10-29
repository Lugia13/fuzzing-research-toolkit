#!/usr/bin/env python3
"""
crash_dedup.py

Reads a directory of crash log files (ASan, UBSan, or gdb "bt" output,
one log per crashing input) and groups them by fault signature instead
of by filename, so a few hundred crash logs from a fuzzing run collapse
down to the handful of distinct bugs they actually represent.

The fault signature is built from the fault type plus the top few stack
frames at the point of the crash, with addresses and other run specific
noise stripped out, so the same bug found through different mutation
paths still lands in the same bucket.

Usage:
    python3 crash_dedup.py <crash_log_directory> [frame_depth]

frame_depth defaults to 3 and controls how many stack frames are used
to build the signature. A lower number groups more aggressively (more
bugs treated as the same); a higher number splits more finely.

No third party dependencies.
"""

import os
import re
import sys
from collections import defaultdict

# Matches ASan/UBSan frame lines like:
#   #0 0x55d... in parse_record /path/to/file.c:142:9
# and gdb "bt" frame lines like:
#   #0  0x0000555... in parse_record (buf=..., len=140) at file.c:142
FRAME_RE = re.compile(
    r"^\s*#\d+\s+(?:0x[0-9a-fA-F]+\s+in\s+)?([A-Za-z_][\w:~<>,. ]*?)\s*(?:\(|$|\s+at\s+|\s+/)"
)

FAULT_TYPE_PATTERNS = [
    (re.compile(r"heap-buffer-overflow", re.I), "heap-buffer-overflow"),
    (re.compile(r"heap-use-after-free", re.I), "use-after-free"),
    (re.compile(r"stack-buffer-overflow", re.I), "stack-buffer-overflow"),
    (re.compile(r"global-buffer-overflow", re.I), "global-buffer-overflow"),
    (re.compile(r"SEGV on unknown address 0x0+\b|null pointer", re.I), "null-deref"),
    # Matches SIGSEGV and plain SEGV. A plain \bSEGV\b would miss SIGSEGV
    # entirely: SEGV is embedded inside SIGSEGV with no word boundary
    # between SIG and SEGV, since both sides are letters.
    (re.compile(r"SIGSEGV|\bSEGV\b", re.I), "segv"),
    (re.compile(r"integer overflow", re.I), "integer-overflow"),
    (re.compile(r"division by zero|divide by zero", re.I), "div-by-zero"),
    (re.compile(r"stack-overflow", re.I), "stack-exhaustion"),
    (re.compile(r"\babort\b", re.I), "abort"),
]


def extract_fault_type(text):
    for pattern, label in FAULT_TYPE_PATTERNS:
        if pattern.search(text):
            return label
    return "unknown"


def extract_frames(text, depth):
    frames = []
    for line in text.splitlines():
        m = FRAME_RE.match(line)
        if m:
            name = m.group(1).strip()
            # Strip template/argument noise that varies run to run but
            # doesn't change which function actually crashed.
            name = re.sub(r"<.*?>", "", name)
            frames.append(name)
        if len(frames) >= depth:
            break
    return frames


def build_signature(text, depth):
    fault_type = extract_fault_type(text)
    frames = extract_frames(text, depth)
    if not frames:
        return f"{fault_type}|no-stack-frames-found"
    return f"{fault_type}|" + ">".join(frames)


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <crash_log_directory> [frame_depth]", file=sys.stderr)
        sys.exit(1)
    log_dir = sys.argv[1]
    depth = int(sys.argv[2]) if len(sys.argv) > 2 else 3

    if not os.path.isdir(log_dir):
        print(f"Not a directory: {log_dir}", file=sys.stderr)
        sys.exit(1)

    buckets = defaultdict(list)
    for fname in sorted(os.listdir(log_dir)):
        fpath = os.path.join(log_dir, fname)
        if not os.path.isfile(fpath):
            continue
        with open(fpath, "r", errors="ignore") as f:
            text = f.read()
        sig = build_signature(text, depth)
        buckets[sig].append(fname)

    print(f"{len(buckets)} distinct fault signature(s) across "
          f"{sum(len(v) for v in buckets.values())} crash log(s)\n")

    for sig, files in sorted(buckets.items(), key=lambda kv: -len(kv[1])):
        print(f"[{len(files)} crash(es)] {sig}")
        for fname in files[:5]:
            print(f"    {fname}")
        if len(files) > 5:
            print(f"    ... and {len(files) - 5} more")
        print()


if __name__ == "__main__":
    main()
