Minimization and regression

A raw crashing input straight out of a fuzzer is often thousands of bytes long, most of which have nothing to do with why it crashes. Minimizing it down to the smallest input that still triggers the same fault makes the bug far easier to understand, far easier to explain in a report, and far easier to turn into a regression test afterward.

Why minimization matters beyond just a shorter report

A ten thousand byte crashing input makes it genuinely hard to tell, just by looking at it, which part of the input actually matters. A fifty byte minimized version usually makes the responsible field obvious on sight. This isn't just about making the write up shorter. It directly speeds up root cause analysis, since there's far less input to read through when tracing what the parser actually did with it.

How minimization actually works

Both AFL++ (through afl-tmin) and libFuzzer (through its own minimize mode) work the same basic way: try removing or simplifying a chunk of the input, rerun it, and check whether it still produces the same crash. If it does, keep the smaller version and repeat. If it doesn't, put that chunk back and try a different reduction. This is a search, not a single pass, and on a large or slow target it can take a while, which is worth planning for rather than being surprised by.

Confirm the crash is actually still the same bug

A minimizer's job is to keep reducing as long as the target still crashes, but it has no idea whether the crash after reduction is the same bug as the crash before it. Always recheck the fault signature, the same stack trace comparison used in triage, after minimization finishes, not just whether the target still crashes at all. It's not rare for aggressive minimization to accidentally wander into triggering a second, different bug partway through the reduction process.

Turn the minimized crash into a regression test

Once a bug is fixed, the minimized input is exactly what should go into a regression test, since it's small, it's fast to run, and it's already proven to trigger the specific fault being fixed. A regression suite built from a project's history of minimized crashes is one of the most effective ways to make sure an old bug doesn't quietly come back in a later refactor.

When minimization isn't worth running

For a crash that's about to be deduplicated away as a near duplicate of a bug you've already minimized, don't bother. Minimize one representative input per bucket after triage and deduplication are done, not every single crashing file a long fuzzing run happened to produce.
