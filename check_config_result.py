#!/usr/bin/env python3
"""Evaluate Home Assistant check_config output for the action."""

from __future__ import annotations

from pathlib import Path
import sys


CONFIG_ERROR_MARKER = "ERROR:homeassistant.config:"


def config_error_lines(log_path: Path) -> list[str]:
    return [
        line
        for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines()
        if CONFIG_ERROR_MARKER in line
    ]


def evaluate(check_exit_code: int, strict: bool, log_path: Path) -> int:
    if check_exit_code != 0:
        print(
            f"Home Assistant check_config exited with status {check_exit_code}.",
            file=sys.stderr,
        )
        return check_exit_code

    if not strict:
        return 0

    errors = config_error_lines(log_path)
    if errors:
        print(
            "Home Assistant reported configuration errors even though "
            "check_config exited successfully:",
            file=sys.stderr,
        )
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    return 0


def parse_strict(value: str) -> bool:
    return value.lower() == "true"


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        print(
            "Usage: check_config_result.py CHECK_CONFIG_EXIT_CODE STRICT LOG_FILE",
            file=sys.stderr,
        )
        return 2

    try:
        check_exit_code = int(argv[1])
    except ValueError:
        print(f"Invalid check_config exit code: {argv[1]!r}", file=sys.stderr)
        return 2

    return evaluate(check_exit_code, parse_strict(argv[2]), Path(argv[3]))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
