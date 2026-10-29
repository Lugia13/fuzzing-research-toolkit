Harness design

The harness is the single most important piece of a fuzzing setup, and it's also the piece people rush the most to get to the actual fuzzing. A bad harness produces results that look busy but mean nothing: crashes that don't reproduce outside the fuzzer, coverage that never gets past the first few functions, or a fuzzer that technically runs for days without ever reaching the code you actually care about.

Isolate the real input boundary

Find the smallest function or entry point that actually receives attacker controlled bytes, not the whole program. If a parser function takes a buffer and a length, fuzz that function directly instead of fuzzing the command line tool that eventually calls it. Every layer you fuzz through instead of fuzzing directly costs you speed, since the fuzzer has to work through file I/O, argument parsing, and setup code on every single iteration just to reach the part that matters.

Reset state between iterations

This is the most common way a harness quietly produces garbage results. If the function under test mutates global state, caches something, or depends on the result of a previous call, iteration two of the fuzz loop isn't testing the same thing iteration one tested. In libFuzzer's in process mode this matters even more, since the whole point is running thousands of iterations in a single process without restarting it. Any state that leaks across iterations either produces false crashes that don't reproduce standalone, or hides real crashes behind state that happens to mask them.

Match what the real caller actually does

A harness that calls the target function with different preconditions than the real application uses will find bugs that are either unreachable in practice or miss the real crash conditions entirely. If the real code always null terminates its buffers before calling the parser, and your harness doesn't, you'll find a class of crash that's real on paper but not reachable through the application's actual API.

Decide what counts as a crash

A segfault is obviously a crash. A call to abort from inside an assertion might or might not be, depending on whether that assertion is meant to catch programmer error during development or is actually enforcing a security relevant invariant at runtime. Decide this explicitly before fuzzing starts, since otherwise you'll spend triage time arguing with yourself about whether every assertion failure is worth reporting.

A minimal libFuzzer style harness

A fuzzing entry point generally needs three things: take a pointer and a length, do whatever setup the real code requires before calling the target function, and make sure nothing from this call leaks into the next one. See harnesses/libfuzzer_template.c for a working skeleton built around those three requirements, including a comment at each point where target specific logic needs to go.

Why this ordering matters

Everything downstream of the harness, corpus quality, how fast the fuzzer explores new code paths, and whether a crash is real or an artifact, depends on getting these four things right first. Time spent fixing a bad harness after a week of fuzzing against it is nearly always time wasted, since you'll need to refuzz from scratch once the harness is actually sound.
