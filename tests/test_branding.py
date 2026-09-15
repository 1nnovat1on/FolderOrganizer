import unittest


class BrandingTests(unittest.TestCase):
    def test_window_title_uses_exact_abstergo_brand(self):
        from folder_organizer.app import WINDOW_TITLE

        self.assertEqual("Abstergo LLC Folder Organizer", WINDOW_TITLE)


if __name__ == "__main__":
    unittest.main()
