"""Keep the hub directory and tracked status page aligned."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PORTS = (
    "Don-t-OpenYourVita",
    "Sakura-Succubus-Vita",
    "Sakura-Succubus-2-Vita",
    "Sakura-Succubus-3-Vita",
    "Sakura-Succubus-4-Vita",
    "Magical-Literary-Heroine-Natsuki-Saves-The-Literature-Club-Vita",
    "HIKE-BACK-Vita",
)


class PortDirectoryTests(unittest.TestCase):
    def test_readme_and_status_page_link_every_owned_port(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        status = (ROOT / "wiki-source" / "Port-Status.md").read_text(encoding="utf-8")
        for repository in PORTS:
            url = f"https://github.com/SilverCrow2323/{repository}"
            with self.subTest(repository=repository):
                self.assertIn(url, readme)
                self.assertIn(url, status)

    def test_harvest_collaboration_is_not_mislabeled_as_an_owned_port(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("https://github.com/takoyaki99/Harvest-December-Reharvested-Portable", readme)
        self.assertNotIn(
            "https://github.com/SilverCrow2323/Harvest-December-Reharvested-Portable",
            readme,
        )

    def test_test_checklist_requires_build_identity_and_evidence(self):
        checklist = (ROOT / "wiki-source" / "Testing-Checklist.md").read_text(encoding="utf-8").lower()
        for term in ("game title", "exact release/build", "ren'py vita", "screenshots", "copyrighted game assets"):
            with self.subTest(term=term):
                self.assertIn(term, checklist)


if __name__ == "__main__":
    unittest.main()
