Crash triage and deduplication

A fuzzer that's been running for a day can easily produce hundreds of crashing inputs. Almost all of them are usually the same handful of bugs, found over and over through slightly different mutation paths. Treating each crashing file as a separate finding wastes enormous amounts of time and, if you actually submit them that way, makes a program's triage team trust your reports less rather than more.

Bucket by the fault, not by the input

The right identity for a crash is where it actually happened, not which file triggered it. For a native crash, that usually means the top few frames of the stack trace at the point of the fault, since the exact frame that crashes and the two or three frames above it are what actually distinguish one bug from another. Two inputs that crash at the same function with the same call stack are almost certainly the same bug even if the inputs themselves look nothing alike. See scripts/crash_dedup.py, which reads a batch of crash logs, extracts a fault signature from each one, and groups them by that signature instead of by filename.

Classify what kind of bug it actually is

A sanitizer report usually tells you directly: heap buffer overflow, use after free, null pointer dereference, stack buffer overflow, integer overflow leading to a bad allocation size. Without a sanitizer, a plain segfault needs a quick look in gdb to figure out whether the faulting instruction is reading or writing, and whether the faulting address looks like a null pointer, a small offset from null, or something that looks like heap or stack memory that's simply out of bounds. scripts/triage_report.py automates the common parts of this: it parses ASan, UBSan, or gdb output and produces a short classification plus the fault signature used for deduplication.

Separate real bugs from fuzzer artifacts

Not every crash is a bug in the target. A harness with a memory leak in its own setup code, a sanitizer timeout that isn't really a hang in the target, or a crash caused by the harness itself rather than the code under test are all things that show up in a crash directory and need to be filtered out before triage, not after a report has already been written. When a crash looks suspicious, the fastest check is usually running the same input directly against the real application outside the fuzzing harness, not just inside it.

Confirm reproducibility before anything else

A crash that only happens inside the fuzzer and never reproduces when you run the same input again, ideally more than once, probably depends on uninitialized memory, a race condition, or harness state that isn't actually deterministic. These are real findings sometimes, but they need to be labeled as what they are rather than written up as a straightforward, reliably reproducible crash.

Keep one representative input per bucket

Once crashes are grouped by fault signature, keep the smallest or cleanest input from each bucket and set the rest aside. This is what you minimize and actually write up. See methodology/05-minimization-and-regression.md for reducing that representative input down to the smallest version that still reproduces the same crash.
