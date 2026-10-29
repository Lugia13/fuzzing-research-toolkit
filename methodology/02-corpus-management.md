Corpus management

A fuzzer is only as good as the seeds it starts from. Coverage guided fuzzers work by mutating existing inputs and keeping the mutations that reach new code, which means every path the fuzzer will ever explore has to start from something already in the corpus or a mutation close enough to it to be reachable in a reasonable number of steps. A weak seed corpus is the single biggest reason a fuzzing campaign stalls after finding the same ten crashes in the first hour and nothing new for the next three days.

Start from real, diverse inputs

Collect actual valid inputs the target is meant to handle. For a file format, that means real files of that format from as many different sources and tools as you can find, not just one sample file duplicated five times. For a protocol, that means real captured traffic, not one hand written example. The goal is to cover as much of the format's actual structure as the fuzzer will need to understand before it can start finding anything new through mutation alone.

Minimize before you fuzz, not after

Once you have a pile of candidate seeds, run them through a coverage based minimizer (the afl-cmin tool that ships with AFL++, or a merge pass for libFuzzer) before starting the real fuzzing run. This keeps only the inputs that contribute genuinely new coverage, which means every seed in the corpus is pulling its weight instead of wasting mutation budget on near duplicates of each other. See scripts/corpus_minimize.sh for a wrapper that handles the common cases.

Grow the corpus during the run, not just before it

Most fuzzers already save new coverage increasing inputs back into the corpus automatically, but it's worth periodically reviewing what's actually been added. If the corpus balloons with thousands of near identical inputs that all trigger the same shallow code path, consider re minimizing partway through a long campaign rather than letting the fuzzer's own mutation engine spend its time reprocessing redundant seeds.

Seed from the edges, not just the common case

Valid inputs at the boundary of what's allowed, the largest size the format supports, the smallest, the deepest nesting level, an input using every optional field at once, tend to exercise code paths that a "typical" valid input never touches. These edge seeds are often worth constructing deliberately rather than waiting for the fuzzer to stumble onto them through random mutation, especially for formats with deep structural nesting where reaching real depth through mutation alone can take a very long time.

Building a starting corpus when you don't have one

When no real sample inputs are available, scripts/seed_corpus_builder.py takes a handful of hand written examples and expands them into a more structurally diverse set using small, targeted mutations, rather than starting a fuzzing run from one or two seeds and hoping the fuzzer's own mutation strategy discovers the format's structure entirely on its own.
