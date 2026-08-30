"""
CLI tests for generate_srt.py's flag parsing and combination rules.

These invoke generate_srt.py as a real subprocess, the same way a user runs
it, against a live DaVinci Resolve instance. That's deliberate: the script
performs Resolve path validation as a side effect of import, so faking that
out would test something other than the real thing. Requires Resolve to be
running with a project open, same as normal use of the script.

Run with: python3 -m pytest tests/ -v
"""
import os
import subprocess
import sys

SCRIPT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "generate_srt.py")


def run(args, timeout=60):
    """Run generate_srt.py with the given args, return CompletedProcess."""
    return subprocess.run(
        [sys.executable, SCRIPT, *args],
        capture_output=True,
        text=True,
        timeout=timeout,
    )


class TestGlobalFlagOrderIndependence:
    def test_verbose_after_file(self):
        result = run(["--list", "--verbose"])
        assert "standalone" not in result.stdout

    def test_verbose_before_list(self):
        result = run(["--verbose", "--list"])
        assert "standalone" not in result.stdout

    def test_short_verbose_after_list(self):
        result = run(["--list", "-v"])
        assert "standalone" not in result.stdout

    def test_short_verbose_before_list(self):
        result = run(["-v", "--list"])
        assert "standalone" not in result.stdout


class TestListFlagStandalone:
    def test_list_rejects_extra_file(self):
        result = run(["nonexistent.m4a", "--list"])
        assert result.returncode == 1
        assert "standalone" in result.stdout

    def test_list_rejects_file_before_and_after(self):
        result = run(["--list", "nonexistent.m4a"])
        assert result.returncode == 1
        assert "standalone" in result.stdout

    def test_list_rejects_concat(self):
        result = run(["--list", "--concat"])
        assert result.returncode == 1
        assert "standalone" in result.stdout

    def test_list_rejects_export(self):
        result = run(["--list", "--export"])
        assert result.returncode == 1
        assert "standalone" in result.stdout

    def test_list_rejects_import(self):
        result = run(["--list", "--import"])
        assert result.returncode == 1
        assert "standalone" in result.stdout

    def test_list_rejects_unrecognized_flag_before_it(self):
        result = run(["--bogus", "--list"])
        assert result.returncode == 1

    def test_list_alone_does_not_hit_standalone_error(self):
        result = run(["--list"])
        assert "standalone" not in result.stdout


class TestUnrecognizedFlags:
    def test_unrecognized_flag_after_file_errors(self):
        result = run(["nonexistent.m4a", "--totally-not-a-flag"])
        assert result.returncode == 1
        assert "Unrecognized flag" in result.stdout

    def test_unrecognized_flag_before_file_errors(self):
        result = run(["--totally-not-a-flag", "nonexistent.m4a"])
        assert result.returncode == 1
        assert "Unrecognized flag" in result.stdout

    def test_typo_of_known_flag_not_swallowed_as_filename(self):
        # Missing trailing 'e' - must not be silently treated as a source file
        result = run(["nonexistent.m4a", "--verbos"])
        assert result.returncode == 1
        assert "Unrecognized flag" in result.stdout

    def test_known_convert_flag_not_rejected(self):
        # --wav is a real flag; should not trip the unrecognized-flag path.
        # (Will still fail later since nonexistent.m4a doesn't exist, but not
        # with "Unrecognized flag".)
        result = run(["nonexistent.m4a", "--wav"])
        assert "Unrecognized flag" not in result.stdout


class TestVerboseOutputLevel:
    def test_quiet_by_default(self):
        result = run(["--list"])
        assert "FINAL PATH CONFIGURATION" not in result.stderr
        assert "=== Starting path validation ===" not in result.stdout

    def test_verbose_shows_diagnostics(self):
        result = run(["--list", "--verbose"])
        assert (
            "FINAL PATH CONFIGURATION" in result.stderr
            or "=== Starting path validation ===" in result.stdout
        )
