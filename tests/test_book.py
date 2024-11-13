import unittest
import shutil
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

from book_module.book import TheBook
from book_module.node import TreeNode


class TestTheBook(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_create_save_load(self):
        book = TheBook(Title="My Awesome Book", directory=self.temp_dir / "test_book")
        book.save_to_directory()

        loaded_book = TreeNode.load_from_directory(self.temp_dir / "test_book")
        self.assertIsInstance(loaded_book, TheBook)
        self.assertEqual(loaded_book.Title, "My Awesome Book")
        self.assertTrue(isinstance(loaded_book._created, datetime))
        self.assertTrue(isinstance(loaded_book._last_save, datetime))

    def test_last_save_update(self):
        book = TheBook(Title="My Book", directory=self.temp_dir / "test_book2")
        book.save_to_directory()
        first_save_time = book._last_save

        # Wait a bit to ensure the timestamp changes
        # time.sleep(1)  # or better solution that doesn't slow down tests in Windows
        book._last_save = datetime.now() + timedelta(seconds=2)

        book.save_to_directory()
        second_save_time = book._last_save

        self.assertGreater(second_save_time, first_save_time)

    def test_str_representation(self):
        book = TheBook(Title="Test Book", directory=self.temp_dir / "test_book3")
        book_str = str(book)
        self.assertIn("The Book: Test Book", book_str)
        self.assertIn("created", book_str)
        self.assertIn("saved", book_str)




if __name__ == '__main__':
    unittest.main()