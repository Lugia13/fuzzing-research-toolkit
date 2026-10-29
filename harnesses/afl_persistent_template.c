/*
 * afl_persistent_template.c
 *
 * A minimal AFL++ persistent mode harness skeleton. Persistent mode
 * runs many iterations inside one process instead of forking per
 * input, which is dramatically faster but means the same state
 * leakage concerns from the libFuzzer template apply here too, and
 * matter even more since a single hung or corrupted process state can
 * silently affect every iteration until AFL++ decides to restart it.
 *
 * Build:
 *   afl-clang-fast -g -O1 afl_persistent_template.c \
 *       -I/path/to/target/include -L/path/to/target/lib -ltarget \
 *       -o fuzz_target
 *
 * Run:
 *   afl-fuzz -i corpus_dir -o findings_dir -- ./fuzz_target
 *
 * See methodology/01-harness-design.md for the reasoning behind each
 * section below.
 */

#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>

/* TODO: include the real target's header(s) here. */
/* #include "target_parser.h" */

#ifndef __AFL_FUZZ_TESTCASE_LEN
/*
 * Fallback definitions so this file can still be built and syntax
 * checked with a plain compiler, outside the afl-clang-fast toolchain.
 * These are no-ops; real persistent mode behavior only exists when
 * actually built with afl-clang-fast or afl-gcc-fast.
 */
#define __AFL_FUZZ_INIT() static uint8_t afl_fallback_buf[1024 * 1024]
#define __AFL_FUZZ_TESTCASE_LEN 0
#define __AFL_FUZZ_TESTCASE_BUF afl_fallback_buf
#define __AFL_LOOP(x) (0)
#define __AFL_INIT() ((void)0)
#endif

__AFL_FUZZ_INIT();

/*
 * TODO: per iteration target call, matching exactly what the real
 * calling code does before and after reaching the function under
 * test. Keep this in sync with the libFuzzer template's
 * LLVMFuzzerTestOneInput if the same target is fuzzed with both.
 */
static void run_one_iteration(const uint8_t *data, size_t size) {
    if (size == 0) {
        return;
    }

    /* TODO: call the actual function under test. */
    /* parse_record(data, size); */

    /*
     * TODO: reset or free anything the target allocated or mutated,
     * so the next iteration starts from the same clean state as the
     * first one did.
     */
}

int main(void) {
    __AFL_INIT();

    unsigned char *buf = __AFL_FUZZ_TESTCASE_BUF;

    while (__AFL_LOOP(10000)) {
        int len = __AFL_FUZZ_TESTCASE_LEN;
        if (len < 0) {
            continue;
        }
        run_one_iteration(buf, (size_t)len);
    }

    return 0;
}
