/*
 * libfuzzer_template.c
 *
 * A minimal libFuzzer harness skeleton. Fill in the three marked
 * sections for a real target; everything else is boilerplate that
 * rarely needs to change.
 *
 * Build (once the TODOs below are filled in):
 *   clang -g -O1 -fsanitize=fuzzer,address libfuzzer_template.c \
 *       -I/path/to/target/include -L/path/to/target/lib -ltarget \
 *       -o fuzz_target
 *
 * Run:
 *   ./fuzz_target corpus_dir/
 *
 * See methodology/01-harness-design.md for the reasoning behind each
 * section below.
 */

#include <stdint.h>
#include <stddef.h>
#include <string.h>

/* TODO: include the real target's header(s) here. */
/* #include "target_parser.h" */

/*
 * TODO: one time setup that only needs to run once, not per iteration.
 * Use LLVMFuzzerInitialize for this if the target needs any kind of
 * global initialization before parsing can happen at all (for example,
 * loading a schema or registering a codec table). Leave this function
 * out entirely if no one time setup is needed.
 */
/*
int LLVMFuzzerInitialize(int *argc, char ***argv) {
    return 0;
}
*/

int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    /*
     * Guard against degenerate inputs the real target would never
     * actually see, so the fuzzer doesn't spend its budget on cases
     * that aren't meaningful. Adjust or remove this if a zero length
     * input is a real, valid case for the target.
     */
    if (size == 0) {
        return 0;
    }

    /*
     * TODO: set up any per iteration state the real target needs
     * before parsing, matching exactly what the real calling code
     * does before it reaches the target function. If the target
     * expects a null terminated buffer and the real caller always
     * null terminates it, do the same here rather than passing the
     * raw libFuzzer buffer directly.
     */

    /* TODO: call the actual function under test. */
    /* parse_record(data, size); */

    /*
     * TODO: tear down or reset any state the target mutated, so the
     * next iteration starts clean. This matters most for in process
     * fuzzing where the same process handles every iteration; state
     * that leaks across iterations produces crashes that don't
     * reproduce when the same input is run again on its own, and can
     * also mask real bugs behind stale state.
     */

    return 0;
}
