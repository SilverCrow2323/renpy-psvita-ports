from __future__ import annotations

import unittest

from renpy_vita_studio.build_plan import get_build_plan


class BuildPlanTests(unittest.TestCase):
    def test_default_plan_contains_both_separate_profiles(self):
        report = get_build_plan()
        self.assertEqual(report["execution_status"], "documentation-only")
        self.assertEqual({item["profile_id"] for item in report["profiles"]}, {"sonicmastr-python27", "grimiku-python311"})

    def test_legacy_plan_keeps_python27_and_unpinned_cython_explicit(self):
        plan = get_build_plan("sonicmastr-python27")
        self.assertTrue(any("2.7.18" in item["requirement"] for item in plan["preflight"]))
        self.assertTrue(any("exact pin is not stated" in item["requirement"] for item in plan["preflight"]))
        self.assertTrue(plan["manual_blockers"])

    def test_python311_plan_pins_cython_and_marks_patched_dependencies(self):
        plan = get_build_plan("grimiku-python311")
        self.assertTrue(any("0.29.37" in item["requirement"] for item in plan["preflight"]))
        self.assertTrue(any(item["item"] == "CPython Vita fork" for item in plan["preflight"]))
        self.assertTrue(any("never executed" in item for item in plan["manual_blockers"]))

    def test_unknown_profile_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unknown profile"):
            get_build_plan("made-up-runtime")

    def test_plan_is_documentation_only(self):
        for profile_id in ("sonicmastr-python27", "grimiku-python311"):
            plan = get_build_plan(profile_id)
            self.assertEqual(plan["execution_status"], "documentation-only")
            self.assertIn("not a compatibility verdict", plan["warning"])


if __name__ == "__main__":
    unittest.main()
