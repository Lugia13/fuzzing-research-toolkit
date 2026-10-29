#!/usr/bin/env python3
"""
triage_report.py

Reads a single crash log (ASan, UBSan, or gdb output) and prints a short
triage summary: what kind of bug it probably is, the fault signature to
use for deduplication against other crashes, and a one line note on what
to check next. This is meant to save the first few minutes of every
triage pass, not to replace actually reading the crash.

Usage:
    python3 triage_report.py <crash_log_file> [frame_depth]
"""

import re
import sys

FRAME_RE = re.compile(
    r"^\s*#\d+\s+(?:0x[0-9a-fA-F]+\s+in\s+)?([A-Za-z_][\w:~<>,. ]*?)\s*(?:\(|$|\s+at\s+|\s+/)"
)

# (pattern, label, next-step note)
FAULT_TYPES = [
    (re.compile(r"heap-buffer-overflow", re.I), "heap-buffer-overflow",
     "Check whether the read/write offset is attacker controlled and whether "
     "a bounds check exists but uses the wrong comparison (off by one is common)."),
    (re.compile(r"heap-use-after-free", re.I), "use-after-free",
     "Find where the object is freed and trace every path that could still "
     "hold a reference to it afterward, not just the one the crash happened to take."),
    (re.compile(r"stack-buffer-overflow", re.I), "stack-buffer-overflow",
     "Check the declared size of the stack buffer against the actual copy or "
     "write length; look for a missing or incorrect length check before the write."),
    (re.compile(r"global-buffer-overflow", re.I), "global-buffer-overflow",
     "Check indexing into the global array or table; a global often means the "
     "index itself is attacker controlled rather than the buffer size being wrong."),
    (re.compile(r"SEGV on unknown address 0x0+\b", re.I), "null-deref",
     "Trace where the pointer was supposed to be set and find the path that "
     "skips that initialization, rather than assuming it's simply unchecked."),
    (re.compile(r"SIGSEGV|\bSEGV\b", re.I), "segv",
     "No sanitizer output available; open the input in gdb with the same "
     "binary and run bt full to get the faulting frame and register state."),
    (re.compile(r"integer overflow", re.I), "integer-overflow",
     "Check whether the overflowed value is later used as a size or an index; "
     "that's almost always where the real impact comes from, not the overflow itself."),
    (re.compile(r"division by zero|divide by zero", re.I), "div-by-zero",
     "Usually a low severity denial of service bug; check whether the divisor "
     "comes directly from the input with no validation."),
    (re.compile(r"stack-overflow", re.I), "stack-exhaustion",
     "Check for unbounded or attacker controlled recursion depth, such as "
     "nested structures in a parser with no depth limit."),
    (re.compile(r"\babort\b", re.I), "abort",
     "Find which assertion fired; decide whether it's a development time "
     "sanity check or an invariant that actually matters for security."),
]


def classify(text):
    for pattern, label, note in FAULT_TYPES:
        if pattern.search(text):
            return label, note
    return "unknown", "No recognized fault pattern; read the raw log directly."


def extract_frames(text, depth):
    frames = []
    for line in text.splitlines():
        m = FRAME_RE.match(line)
        if m:
            name = re.sub(r"<.*?>", "", m.group(1).strip())
            frames.append(name)
        if len(frames) >= depth:
            break
    return frames


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <crash_log_file> [frame_depth]", file=sys.stderr)
        sys.exit(1)
    log_path = sys.argv[1]
    depth = int(sys.argv[2]) if len(sys.argv) > 2 else 3

    with open(log_path, "r", errors="ignore") as f:
        text = f.read()

    fault_type, note = classify(text)
    frames = extract_frames(text, depth)
    signature = f"{fault_type}|" + (">".join(frames) if frames else "no-stack-frames-found")

    print(f"file          {log_path}")
    print(f"fault type    {fault_type}")
    print(f"top frames    {', '.join(frames) if frames else '(none found, log may not be sanitizer/gdb output)'}")
    print(f"signature     {signature}")
    print(f"next step     {note}")


if __name__ == "__main__":
    main()
