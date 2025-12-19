import unittest
from media_processor.constant.extensions import VIDEO_EXTENSIONS
from media_processor.runner.batch_audio_runner import is_video_folder as audio_check
from media_processor.runner.batch_merge_runner import is_video_folder as merge_check
from pathlib import Path
import tempfile
import shutil


class TestVideoExtensions(unittest.TestCase):
    def test_extensions_contain_new_types(self):
        """Verify that VIDEO_EXTENSIONS contains the requested types."""
        required = {".rm", ".rmvb", ".mpg", ".wmv", ".webm", ".vob"}
        for ext in required:
            self.assertIn(ext, VIDEO_EXTENSIONS)

    def test_runner_extension_usage(self):
        """Verify that runners actually use the centralized constant."""
        # Create a temp dir with a .rmvb file
        with tempfile.TemporaryDirectory() as tmpdirname:
            root = Path(tmpdirname)
            (root / "test.rmvb").touch()
            (root / "ignore.txt").touch()

            # Check if runners detect it
            self.assertTrue(audio_check(root), "Audio runner should detect .rmvb")
            self.assertTrue(merge_check(root), "Merge runner should detect .rmvb")


if __name__ == "__main__":
    unittest.main()
