import unittest


class CompletionMessageTests(unittest.TestCase):
    def test_completion_message_announces_ding_and_moved_count(self):
        from folder_organizer.app import completion_message

        self.assertEqual(
            "Ding! Complete — organized 3 file(s). Use Undo Last Run to restore them.",
            completion_message(3),
        )


if __name__ == "__main__":
    unittest.main()
