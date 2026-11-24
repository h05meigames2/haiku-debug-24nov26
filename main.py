#!/usr/bin/env python3
"""Write one original haiku about debugging to entry.txt.

The haiku is fixed, self-contained, and validated before writing:
exactly 3 lines, syllable counts 5-7-5, total length at most 200
characters. Pure standard library, no network, deterministic.
"""

import os
import re
import sys

HAIKU = (
    "Cursor blinks at three\n"
    "a lone log line confesses\n"
    "and the bug was me"
)

EXPECTED_SYLLABLES = (5, 7, 5)
MAX_CHARS = 200

VOWELS = "aeiouy"


def count_syllables(word):
    """Estimate the syllable count of one lowercase word.

    Counts groups of consecutive vowels, then discounts a trailing
    silent 'e'. Good enough for the fixed vocabulary used here.
    """
    word = word.lower().strip(".,;:!?\"'()")
    if not word:
        return 0
    count = 0
    prev_vowel = False
    for ch in word:
        is_vowel = ch in VOWELS
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel
    # Silent trailing 'e' (e.g. "lone", "line", "three"): drop one,
    # but never below a single syllable (e.g. "me" still counts as 1).
    if word.endswith("e") and count > 1:
        count -= 1
    return max(count, 1)


def validate(haiku):
    """Raise ValueError unless the haiku meets the bounty rules."""
    lines = haiku.split("\n")
    if len(lines) != 3:
        raise ValueError(f"haiku must have exactly 3 lines, got {len(lines)}")
    if any(not line.strip() for line in lines):
        raise ValueError("haiku lines must not be empty")
    if len(haiku) > MAX_CHARS:
        raise ValueError(
            f"haiku is {len(haiku)} chars, over the {MAX_CHARS} limit"
        )
    for line, expected in zip(lines, EXPECTED_SYLLABLES):
        words = re.findall(r"[A-Za-z']+", line)
        total = sum(count_syllables(w) for w in words)
        if total != expected:
            raise ValueError(
                f"line {line!r} has {total} syllables, expected {expected}"
            )


def main():
    validate(HAIKU)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.txt")
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(HAIKU + "\n")
    # Round-trip check: the file on disk must be exactly the haiku
    # we validated, so a truncated or mangled write cannot slip by.
    with open(out_path, encoding="utf-8") as fh:
        written = fh.read()
    if written != HAIKU + "\n":
        raise ValueError(f"round-trip mismatch in {out_path}")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    try:
        main()
    except ValueError as exc:
        print(f"invalid haiku: {exc}", file=sys.stderr)
        raise SystemExit(1)
