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


class TestShorthandFlags:
    """-c/-e/-i/-l/-v are shorthand for --concat/--export/--import/--list/--verbose,
    and may be bundled behind a single dash (-cv == -c -v)."""

    def test_short_list_alone(self):
        result = run(["-l"])
        assert "standalone" not in result.stdout
        assert result.returncode == 0

    def test_short_verbose_matches_long_form_output(self):
        long_result = run(["--list", "--verbose"])
        short_result = run(["-l", "-v"])
        assert ("FINAL PATH CONFIGURATION" in long_result.stderr) == (
            "FINAL PATH CONFIGURATION" in short_result.stderr
        )

    def test_bundled_list_and_verbose(self):
        result = run(["-lv"])
        assert "standalone" not in result.stdout
        assert "FINAL PATH CONFIGURATION" in result.stderr

    def test_bundled_verbose_and_list_reverse_order(self):
        result = run(["-vl"])
        assert "standalone" not in result.stdout
        assert "FINAL PATH CONFIGURATION" in result.stderr

    def test_bundled_list_and_concat_rejected_as_non_standalone(self):
        # -l plus any other global flag violates --list's standalone rule,
        # same as if they'd been spelled out long-form.
        result = run(["-lc"])
        assert result.returncode == 1
        assert "standalone" in result.stdout

    def test_short_import_and_export_bundle(self):
        result = run(["-ie", "nonexistent.m4a"])
        # Should not be rejected as an unrecognized flag; fails later only
        # because the file doesn't exist / no Resolve project state applies.
        assert "Unrecognized flag" not in result.stdout

    def test_unknown_single_letter_rejected(self):
        result = run(["-x"])
        assert result.returncode == 1
        assert "Unrecognized flag" in result.stdout

    def test_bundle_with_one_bad_letter_rejected(self):
        result = run(["-cx"])
        assert result.returncode == 1
        assert "Unrecognized flag" in result.stdout
        assert "-x" in result.stdout

    def test_shorthand_is_case_insensitive(self):
        # -V (uppercase) must expand the same as -v.
        lower_result = run(["--list", "-v"])
        upper_result = run(["--list", "-V"])
        assert ("FINAL PATH CONFIGURATION" in lower_result.stderr) == (
            "FINAL PATH CONFIGURATION" in upper_result.stderr
        )
        assert "Unrecognized flag" not in upper_result.stdout

    def test_bundled_shorthand_case_insensitive(self):
        result = run(["-CE", "nonexistent.m4a"])
        assert "Unrecognized flag" not in result.stdout

    def test_shorthand_position_independent(self):
        result_a = run(["-l", "-v"])
        result_b = run(["-v", "-l"])
        assert ("standalone" in result_a.stdout) == ("standalone" in result_b.stdout)
        assert result_a.returncode == result_b.returncode

    def test_duplicate_flag_via_short_and_long_is_harmless(self):
        result = run(["-l", "--list"])
        assert result.returncode == 0
        assert "standalone" not in result.stdout

    def test_double_dash_flag_not_treated_as_shorthand_bundle(self):
        # A --long flag must never be run through single-letter expansion.
        result = run(["--list", "--verbose"])
        assert "Unrecognized flag" not in result.stdout


class TestNoArgsUsage:
    def test_no_args_does_not_crash(self):
        result = run([])
        assert result.returncode == 0
        assert "Traceback" not in result.stderr

    def test_no_args_prints_usage(self):
        result = run([])
        assert "Usage:" in result.stdout

    def test_no_args_usage_lists_all_global_flags(self):
        result = run([])
        for flag in ("--concat", "--export", "--import", "--list", "--timelines", "--verbose"):
            assert flag in result.stdout

    def test_no_args_usage_lists_all_shorthand_letters(self):
        result = run([])
        for letter in ("-c", "-e", "-i", "-l", "-t", "-v"):
            assert letter in result.stdout

    def test_no_args_usage_lists_conversion_formats(self):
        result = run([])
        for fmt_flag in ("--wav", "--mp3", "--flac", "--aac", "--ogg", "--opus", "--aiff"):
            assert fmt_flag in result.stdout

    def test_no_args_usage_lists_conv_dir_flag(self):
        result = run([])
        assert "--conv-dir" in result.stdout

    def test_with_args_does_not_print_usage(self):
        result = run(["nonexistent.m4a"])
        assert "Usage:" not in result.stdout


class TestTimelinesFlagStandalone:
    """--timelines (like --list) must be standalone (only --verbose/-v may
    accompany it). These don't need a pty since rejection happens before the
    interactive picker is ever launched."""

    def test_rejects_extra_file(self):
        result = run(["nonexistent.m4a", "--timelines"])
        assert result.returncode == 1
        assert "standalone" in result.stdout

    def test_rejects_concat(self):
        result = run(["--timelines", "--concat"])
        assert result.returncode == 1
        assert "standalone" in result.stdout

    def test_rejects_list(self):
        # --list and --timelines both demand standalone use; combining them
        # must be rejected, not silently pick one.
        result = run(["--list", "--timelines"])
        assert result.returncode == 1
        assert "standalone" in result.stdout

    def test_short_flag_rejects_extra_file(self):
        result = run(["-t", "nonexistent.m4a"])
        assert result.returncode == 1
        assert "standalone" in result.stdout

    def test_bundled_with_concat_rejected(self):
        result = run(["-tc"])
        assert result.returncode == 1
        assert "standalone" in result.stdout

    def test_unrecognized_flag_before_it_rejected(self):
        result = run(["--bogus", "--timelines"])
        assert result.returncode == 1


class TestTimelinesInteractivePicker:
    """Full end-to-end test of the checkbox picker + subtitle-generation
    pipeline, driven through a real pty since questionary/prompt_toolkit
    needs an attached terminal. Requires a live Resolve project open.
    """

    def _run_interactive(self, args, keys, launch_wait=2.0, after_wait=4.0):
        """Launch generate_srt.py with `args` in a pty, send `keys` (bytes)
        after the picker has had time to render, then capture all output.

        Returns (output, returncode). returncode is None if the process was
        still running and had to be force-killed (e.g. an unexpected hang);
        otherwise it's the process's real exit code.
        """
        import pty
        import time

        pid, fd = pty.fork()
        if pid == 0:
            os.execvp(sys.executable, [sys.executable, SCRIPT, *args])

        screen = b""
        returncode = None
        try:
            time.sleep(launch_wait)
            try:
                screen += os.read(fd, 65536)
            except OSError:
                pass

            for chunk in keys:
                os.write(fd, chunk)
                time.sleep(0.3)

            time.sleep(after_wait)
            try:
                screen += os.read(fd, 65536)
            except OSError:
                pass

            done_pid, status = os.waitpid(pid, os.WNOHANG)
            if done_pid == pid:
                returncode = os.waitstatus_to_exitcode(status)
        finally:
            if returncode is None:
                try:
                    os.kill(pid, 9)
                except ProcessLookupError:
                    pass
                os.waitpid(pid, 0)

        return screen.decode(errors="replace"), returncode

    def test_picker_lists_timelines(self):
        # Launch, capture the initial render, then cancel with Ctrl-C so we
        # don't actually run subtitle generation just to check the listing.
        output, _ = self._run_interactive(["--timelines"], keys=[b"\x03"], after_wait=1.0)
        assert "Select timelines" in output

    def test_ctrl_c_cancels_with_exit_1(self):
        output, returncode = self._run_interactive(["--timelines"], keys=[b"\x03"], after_wait=1.0)
        assert "Cancelled" in output
        assert returncode == 1

    def test_case_insensitive_shorthand_uppercase_list(self):
        output, returncode = self._run_interactive(["-L"], keys=[], launch_wait=2.0, after_wait=0.5)
        assert "standalone" not in output
        assert returncode == 0

    def test_case_insensitive_shorthand_uppercase_timelines(self):
        output, _ = self._run_interactive(["-T"], keys=[b"\x03"], after_wait=1.0)
        assert "Select timelines" in output

    def test_no_selection_exits_cleanly(self):
        # Enter with nothing toggled on should report no timelines selected,
        # not crash or hang, and exit 0 (distinct from the Ctrl-C/exit-1 path).
        output, returncode = self._run_interactive(["-t"], keys=[b"\r"], after_wait=1.0)
        assert "No timelines selected" in output
        assert returncode == 0

    def test_selecting_a_timeline_runs_pipeline_not_export(self):
        # Space toggles the first item, enter confirms. Whatever the outcome
        # (a timeline with no audio fails at CreateSubtitlesFromAudio, per
        # Resolve's own validation — that's expected, not a test failure),
        # this must never mention writing/exporting an SRT file.
        output, _ = self._run_interactive(["--timelines"], keys=[b" ", b"\r"])
        assert "Generating subtitles for" in output
        assert "timeline(s) completed" in output
        assert ".srt" not in output.lower()
        assert "export" not in output.lower()
