Fuzzing Research Toolkit

A methodology and set of working scripts for fuzzing across different kinds of targets: native binaries, parsers, web and API inputs, and structured text formats. This isn't a single tool. It's the process I use to go from "I want to fuzz this" to a triaged, deduplicated, minimized set of crashes worth actually reporting.

The toolkit is intentionally not tied to one fuzzer or one language. Coverage guided fuzzing with AFL++ or libFuzzer works well for native code with a clear input boundary. Structured, grammar aware fuzzing works better for formats where random byte flipping rarely produces anything the parser accepts. Both approaches show up here, along with the parts that matter regardless of which one you use: building a seed corpus that actually represents real inputs, telling a genuine crash apart from fuzzer noise, and reducing a thousand crashing inputs down to the handful that are actually distinct bugs.

What this repo documents, not what it found

This repo contains methodology and reusable tooling only. No crashes, no vulnerability details, and no target names from any real engagement are included. Everything here was built to be run against your own test targets, and every script takes a path or a target as an argument rather than assuming anything about what you're fuzzing.

Why fuzzing this way

Most of the actual difficulty in fuzzing isn't running the fuzzer. It's everything around it. A harness that doesn't reset state between iterations gives you crashes that don't reproduce. A corpus that's too small or too uniform means the fuzzer spends its whole budget rediscovering the same three code paths. A triage process that treats every crash as a separate bug means you spend days writing up five reports that are actually the same null pointer dereference. This toolkit is built around the steps that prevent those specific failures.

What's in this repo

methodology holds the written notes: how to design a harness, how to manage and grow a corpus, how to deduplicate and triage crashes, when coverage guided fuzzing is worth the setup cost versus a simpler structured generator, and how to minimize a crash down to the smallest input that still reproduces it.

scripts holds working tools: a crash deduplicator that buckets crashes by their actual fault signature instead of their file name, a triage report generator that reads a sanitizer or gdb crash and classifies what kind of bug it probably is, a corpus minimizer wrapper, and a seed corpus builder that expands a handful of example inputs into a more diverse starting set.

harnesses holds template harnesses: a libFuzzer template and an AFL++ persistent mode template for native targets, plus a Python based structured fuzzer for text and semi structured formats where a coverage guided byte fuzzer tends to waste most of its time on inputs the parser immediately rejects.

Tooling used

AFL++ or libFuzzer for coverage guided native fuzzing, a sanitizer build (ASan, UBSan) for catching memory and undefined behavior bugs as they happen rather than finding out later, gdb for crash inspection, and Python 3 for the scripts, since most of the orchestration and triage work is text processing, not performance sensitive.

Responsible use

Everything here assumes you're fuzzing a target you own, a target you've built yourself for testing, or a target you have explicit authorization to test. The harness templates and scripts take a target path as input and don't fuzz anything on their own.

Author

Oussama Saddati. Portfolio at oussamasaddati.vercel.app.
