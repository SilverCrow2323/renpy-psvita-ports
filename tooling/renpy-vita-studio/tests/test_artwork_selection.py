import tempfile
import unittest
from pathlib import Path

from renpy_vita_studio.artwork_selection import (
    GENERATED_ARTWORK_LABEL, artwork_choices, resolve_artwork_selection,
)


class ArtworkSelectionTests(unittest.TestCase):
    def test_generated_option_is_available_even_without_game_art(self):
        with tempfile.TemporaryDirectory() as temp:
            self.assertEqual(artwork_choices([], temp), [GENERATED_ARTWORK_LABEL])
            self.assertIsNone(resolve_artwork_selection(GENERATED_ARTWORK_LABEL, temp))

    def test_game_images_are_relative_and_generated_is_explicit(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            image = root / "game" / "images" / "cover.png"
            image.parent.mkdir(parents=True)
            image.write_bytes(b"image-placeholder")
            choices = artwork_choices([image], root / "game")
            self.assertEqual(choices, [GENERATED_ARTWORK_LABEL, "images/cover.png"])
            self.assertEqual(resolve_artwork_selection("images/cover.png", root / "game"), image.resolve())

    def test_external_image_path_is_supported(self):
        with tempfile.TemporaryDirectory() as temp:
            image = Path(temp) / "outside.png"
            image.write_bytes(b"image-placeholder")
            self.assertEqual(resolve_artwork_selection(str(image), temp), image.resolve())

    def test_missing_image_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, "does not exist"):
                resolve_artwork_selection("missing.png", temp)


if __name__ == "__main__":
    unittest.main()
