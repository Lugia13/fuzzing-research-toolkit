#!/usr/bin/env bash
#
# corpus_minimize.sh
#
# Wrapper around a coverage based corpus minimizer. Detects whether
# afl-cmin (AFL++) or a libFuzzer compatible binary is being used and
# runs the matching minimization command, instead of needing to remember
# two different tools' argument order every time.
#
# Usage:
#   ./corpus_minimize.sh afl <target_binary> <input_corpus_dir> <output_corpus_dir>
#   ./corpus_minimize.sh libfuzzer <fuzzer_binary> <input_corpus_dir>
#
# For AFL++, output_corpus_dir is where the minimized corpus is written;
# input_corpus_dir is left untouched. For libFuzzer, the fuzzer binary's
# merge mode writes the minimized result back into input_corpus_dir
# itself, which matches libFuzzer's own merge semantics.
#
# Requires: afl-cmin on PATH (for the afl mode), or a libFuzzer
# instrumented binary (for the libfuzzer mode).

set -euo pipefail

MODE="${1:?Usage: $0 <afl|libfuzzer> <binary> <input_dir> [output_dir]}"

case "$MODE" in
  afl)
    TARGET_BIN="${2:?Usage: $0 afl <target_binary> <input_corpus_dir> <output_corpus_dir>}"
    INPUT_DIR="${3:?Usage: $0 afl <target_binary> <input_corpus_dir> <output_corpus_dir>}"
    OUTPUT_DIR="${4:?Usage: $0 afl <target_binary> <input_corpus_dir> <output_corpus_dir>}"

    if ! command -v afl-cmin >/dev/null 2>&1; then
      echo "afl-cmin not found on PATH. Install AFL++ first." >&2
      exit 1
    fi

    mkdir -p "$OUTPUT_DIR"
    BEFORE_COUNT=$(find "$INPUT_DIR" -type f | wc -l)
    afl-cmin -i "$INPUT_DIR" -o "$OUTPUT_DIR" -- "$TARGET_BIN" @@
    AFTER_COUNT=$(find "$OUTPUT_DIR" -type f | wc -l)
    echo "Minimized corpus: ${BEFORE_COUNT} input(s) down to ${AFTER_COUNT} input(s)."
    ;;

  libfuzzer)
    FUZZER_BIN="${2:?Usage: $0 libfuzzer <fuzzer_binary> <input_corpus_dir>}"
    INPUT_DIR="${3:?Usage: $0 libfuzzer <fuzzer_binary> <input_corpus_dir>}"

    if [[ ! -x "$FUZZER_BIN" ]]; then
      echo "Fuzzer binary not found or not executable: $FUZZER_BIN" >&2
      exit 1
    fi

    MERGE_DIR=$(mktemp -d)
    BEFORE_COUNT=$(find "$INPUT_DIR" -type f | wc -l)
    "$FUZZER_BIN" -merge=1 "$MERGE_DIR" "$INPUT_DIR"
    rm -rf "$INPUT_DIR"
    mv "$MERGE_DIR" "$INPUT_DIR"
    AFTER_COUNT=$(find "$INPUT_DIR" -type f | wc -l)
    echo "Minimized corpus in place: ${BEFORE_COUNT} input(s) down to ${AFTER_COUNT} input(s)."
    ;;

  *)
    echo "Unknown mode: $MODE (expected 'afl' or 'libfuzzer')" >&2
    exit 1
    ;;
esac
