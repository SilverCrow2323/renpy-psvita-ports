from __future__ import annotations

import unittest

from renpy_vita_studio.runtime_profiles import assess_runtime_profile, list_runtime_profiles


class RuntimeProfileTests(unittest.TestCase):
    def test_python27_selects_legacy_reference_candidate(self):
        report = assess_runtime_profile("7.4.11", ["python2.7"])
        self.assertEqual(report["assessment"], "candidate")
        self.assertEqual(report["candidates"][0]["profile_id"], "sonicmastr-python27")

    def test_renpy8_python311_is_a_strong_indicator_not_a_verdict(self):
        report = assess_runtime_profile("8.3.4", ["python3.11"])
        self.assertEqual(report["assessment"], "candidate")
        self.assertEqual(report["candidates"][0]["profile_id"], "grimiku-python311")
        self.assertEqual(report["candidates"][0]["confidence"], "strong-indicator")
        self.assertIn("not proof", report["warning"])

    def test_mixed_python_runtimes_are_ambiguous(self):
        report = assess_runtime_profile(None, ["python2.7", "python3.11"])
        self.assertEqual(report["assessment"], "ambiguous")

    def test_unknown_runtime_stays_unknown(self):
        report = assess_runtime_profile(None, [])
        self.assertEqual(report["assessment"], "unknown")
        self.assertEqual(report["candidates"], [])

    def test_profiles_include_upstream_sources_and_build_requirements(self):
        profiles = list_runtime_profiles()
        self.assertEqual(len(profiles), 2)
        self.assertTrue(all(item["source"].startswith("https://github.com/") for item in profiles))
        self.assertTrue(all(item["requirements"] for item in profiles))


if __name__ == "__main__":
    unittest.main()
