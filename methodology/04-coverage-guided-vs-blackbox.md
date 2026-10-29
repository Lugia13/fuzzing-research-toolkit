Coverage guided fuzzing versus structured generation

Coverage guided fuzzing, the AFL++ and libFuzzer style of mutating inputs and keeping the mutations that reach new code, is the default most people reach for, and for a lot of native targets with a reasonably simple input format it's the right choice. But it isn't always the best tool, and knowing when to reach for a structured or grammar aware generator instead can save days of a fuzzer mutating byte strings that a real parser rejects in the first ten lines of code.

When coverage guided fuzzing works well

Binary formats with a relatively flat structure, simple length prefixed fields, or a format that's forgiving of small bit flips still parsing far enough to reach interesting code, are a good fit. The feedback loop of mutate, measure coverage, keep what helps works because small mutations tend to produce inputs that are still valid enough to get somewhere.

When it struggles

Formats with checksums, magic numbers, or strict structural validation near the start of parsing are brutal for a byte level mutator. If the first four bytes have to match an exact magic number or the parser bails immediately, a byte flipping fuzzer will spend the overwhelming majority of its time generating inputs that never get past that first check. Text based formats with nested structure, JSON like formats, configuration languages, anything with matching brackets or quotes that need to balance, have the same problem: random mutation breaks the structure far more often than it produces something that parses deep enough to be interesting.

Structured generation as the alternative

A grammar aware or structure aware generator builds inputs that are valid by construction, so every generated input gets past the shallow structural checks and spends its fuzzing budget on the logic underneath instead. This trades the fully automatic exploration of coverage guided fuzzing for a generator that needs to actually understand the format, which is more upfront work but often finds deeper bugs far faster for exactly the formats where byte level mutation struggles. See harnesses/python_structured_fuzzer.py for a working example built around a simple nested text format, which can be adapted to a real target format by changing its grammar rules.

A practical middle ground

Grammar aware generation for the structural skeleton of an input, combined with coverage guided mutation applied to the individual field values once the skeleton is valid, often works better than either approach alone. This is more setup than either technique by itself, so it's usually worth trying the simpler approach first and only reaching for a hybrid when a target's structural validation is clearly the bottleneck.

How to tell which one you need

Run a short fuzzing session with a plain coverage guided fuzzer first and watch the coverage graph. If coverage plateaus almost immediately and stays flat, the fuzzer is very likely stuck against a structural check it can't get past through mutation alone, and it's time to switch to or add a structured generator rather than letting the campaign run longer in the hope that it eventually gets lucky.
