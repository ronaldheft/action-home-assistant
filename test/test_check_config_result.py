from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "check_config_result.py"


def load_helper():
    spec = importlib.util.spec_from_file_location("check_config_result", HELPER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class CheckConfigResultTest(unittest.TestCase):
    def run_helper(self, exit_code: int, strict: bool, log: str) -> int:
        helper = load_helper()
        with tempfile.NamedTemporaryFile("w", encoding="utf-8") as log_file:
            log_file.write(log)
            log_file.flush()

            return helper.evaluate(exit_code, strict, Path(log_file.name))

    def test_fails_when_home_assistant_exits_nonzero(self) -> None:
        self.assertEqual(self.run_helper(1, False, "Testing configuration\n"), 1)

    def test_fails_in_strict_mode_when_log_contains_invalid_config(self) -> None:
        log = (
            "Testing configuration at /github/workspace/.\n"
            "2026-06-18T22:46:46.8557874Z ERROR:homeassistant.config:Invalid "
            "config for 'template' at packages/lock.yaml, line 47: "
            "'suggested_display_precision' is an invalid option for 'template'\n"
        )

        self.assertEqual(self.run_helper(0, True, log), 1)

    def test_preserves_non_strict_behavior_for_logged_config_errors(self) -> None:
        log = "ERROR:homeassistant.config:Invalid config for 'template'\n"

        self.assertEqual(self.run_helper(0, False, log), 0)

    def test_allows_other_errors_when_home_assistant_exits_successfully(self) -> None:
        log = (
            "ERROR:homeassistant.components.automation:Automation with alias "
            "'Remote - Dining Room' failed to setup triggers and has been "
            "disabled: Unknown device '4d14a59c0dc525ed0f6da67f610694ca'\n"
        )

        self.assertEqual(self.run_helper(0, True, log), 0)

    def test_passes_clean_successful_check(self) -> None:
        self.assertEqual(self.run_helper(0, True, "Testing configuration\n"), 0)


if __name__ == "__main__":
    unittest.main()
