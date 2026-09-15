import tempfile
import unittest
from pathlib import Path


class PreviewTests(unittest.TestCase):
    def test_preview_groups_top_level_regular_visible_files_by_extension(self):
        from folder_organizer.core import build_preview

        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "report.TXT").write_text("report", encoding="utf-8")
            (root / "photo.jpg").write_text("photo", encoding="utf-8")
            (root / ".private.txt").write_text("hidden", encoding="utf-8")
            (root / "subfolder").mkdir()

            preview = build_preview(root)

        self.assertEqual({"jpg": ["photo.jpg"], "txt": ["report.TXT"]}, preview.groups)
        self.assertEqual(2, preview.file_count)
        self.assertEqual(2, preview.excluded_count)


class OrganizeAndUndoTests(unittest.TestCase):
    def test_confirmed_organization_avoids_overwrite_and_writes_undo_manifest(self):
        from folder_organizer.core import organize_preview

        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "report.txt"
            source.write_text("new", encoding="utf-8")
            destination = root / "txt"
            destination.mkdir()
            (destination / "report.txt").write_text("existing", encoding="utf-8")

            result = organize_preview(root, confirmed=True)

            moved_file = destination / "report (1).txt"
            self.assertFalse(source.exists())
            self.assertEqual("new", moved_file.read_text(encoding="utf-8"))
            self.assertEqual("existing", (destination / "report.txt").read_text(encoding="utf-8"))
            self.assertTrue(result.manifest_path.is_file())
            self.assertEqual(1, len(result.moves))

    def test_unconfirmed_organization_does_not_move_files(self):
        from folder_organizer.core import organize_preview

        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "keep.txt"
            source.write_text("keep", encoding="utf-8")

            result = organize_preview(root, confirmed=False)

            self.assertEqual([], result.moves)
            self.assertTrue(source.is_file())
            self.assertFalse(result.manifest_path.exists())

    def test_undo_last_run_restores_files_and_removes_manifest(self):
        from folder_organizer.core import organize_preview, undo_last_run

        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            original = root / "notes.md"
            original.write_text("notes", encoding="utf-8")
            organize_preview(root, confirmed=True)

            result = undo_last_run(root)

            self.assertEqual(1, result.restored_count)
            self.assertEqual("notes", original.read_text(encoding="utf-8"))
            self.assertFalse((root / ".folderorganizer-last-run.json").exists())
            self.assertFalse((root / "md" / "notes.md").exists())


if __name__ == "__main__":
    unittest.main()
