import unittest
from book_module.node import TreeNode, BaseIntNode, NodeWithChildren
import shutil
from pathlib import Path
import tempfile


class TestTreeNode(unittest.TestCase):
    def setUp(self):
        """Create a temporary directory for testing."""
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Clean up the temporary directory after each test."""
        shutil.rmtree(self.temp_dir)

    def test_valid_property(self):
        # Tests for BaseIntNode
        valid_node = BaseIntNode(value=5, directory=self.temp_dir / "valid")
        invalid_node_str = BaseIntNode(value="5", directory=self.temp_dir / "invalid_str")  # String value
        invalid_node_float = BaseIntNode(value=5.5, directory=self.temp_dir / "invalid_float")  # Float value

        self.assertTrue(valid_node.valid)
        self.assertFalse(invalid_node_str.valid)  # String value should be invalid
        self.assertFalse(invalid_node_float.valid)  # Float value should be invalid

        # Tests for NodeWithChildren
        parent_dir = self.temp_dir / "parent"

        parent = NodeWithChildren(directory=parent_dir)
        parent.save_to_directory(parent_dir)

        self.assertFalse(parent.valid)  # Invalid (no children)

        child1 = BaseIntNode(value=1)
        parent.add_child(child1, "child1")  # Add correct child with correct name

        loaded_parent = TreeNode.load_from_directory(parent_dir)  # reload parent to refresh children
        self.assertTrue(loaded_parent.valid)  # Valid (correct child with correct name)

        # Test with wrong child name *in addition to* correct child
        child2 = BaseIntNode(value=2)
        parent.add_child(child2, "wrong_name")  # Correct type but wrong name
        loaded_parent = TreeNode.load_from_directory(parent_dir)  # reload parent to refresh children

        self.assertTrue(loaded_parent.valid)  # Still valid (required child is present)

        child3 = NodeWithChildren(directory="child3")  # Incorrect type
        parent.add_child(child3, "child1")  # Correct name, wrong type

        loaded_parent = TreeNode.load_from_directory(parent_dir)  # reload to refresh children
        self.assertFalse(loaded_parent.valid)  # Invalid (wrong type)

        parent.remove_child("child1")  # remove using new method

        loaded_parent = TreeNode.load_from_directory(parent_dir)  # reload to refresh children

        self.assertFalse(loaded_parent.valid)  # Invalid again (required child removed)

    def test_get_other_files_and_dirs(self):
        # Test with TreeNode directory
        root = BaseIntNode(value=10, directory=self.temp_dir / "root")
        root.save_to_directory()

        # Create extra files/dirs
        (self.temp_dir / "root" / "file1.txt").touch()
        (self.temp_dir / "root" / "subdir1").mkdir()

        loaded_root = TreeNode.load_from_directory(self.temp_dir / "root")
        other_items_treenode = list(loaded_root.get_other_files_and_dirs())

        self.assertEqual(sorted(other_items_treenode), sorted([("file1.txt", False), ("subdir1", True)]))

        # Test with nested TreeNode directory
        child1 = BaseIntNode(value=20)
        root.add_child(child1, "child1")  # Create a child TreeNode

        (self.temp_dir / "root" / "child1" / "file2.txt").touch()  # File inside child's directory

        loaded_root = TreeNode.load_from_directory(self.temp_dir / "root")  # Reload to refresh children
        other_items_nested = list(loaded_root.get_other_files_and_dirs())

        self.assertEqual(sorted(other_items_nested),
                         sorted([("file1.txt", False), ("subdir1", True)]))  # child1 is TreeNode, so is not included

        # Test with ordinary directory (no node_data.json initially, but added later)
        (self.temp_dir / "root2").mkdir()
        (self.temp_dir / "root2" / "file3.txt").touch()
        (self.temp_dir / "root2" / "subdir2").mkdir()

        loaded_root2 = BaseIntNode(value=10, directory=self.temp_dir / "root2")  # initialize BaseIntNode
        other_items_ordinary_before_save = list(loaded_root2.get_other_files_and_dirs())

        loaded_root2.save_to_directory()  # save node
        other_items_ordinary_after_save = list(loaded_root2.get_other_files_and_dirs())

        self.assertEqual(sorted(other_items_ordinary_before_save),
                         sorted([("file3.txt", False), ("subdir2", True)]))  # Correct expectation before save
        self.assertEqual(sorted(other_items_ordinary_after_save),
                         sorted([("file3.txt", False), ("subdir2", True)]))  # Correct expectation after save

    def test_save_load_single_node(self):
        node = BaseIntNode(value=42, directory=self.temp_dir / "node1")
        node.save_to_directory()
        node_dict = node.to_dict()

        loaded_node = TreeNode.load_from_directory(self.temp_dir / "node1")
        loaded_node_dict = loaded_node.to_dict()
        self.assertEqual(node_dict, loaded_node_dict)
        self.assertIsNotNone(loaded_node)
        self.assertEqual(loaded_node.value, 42)
        self.assertEqual(loaded_node.directory, self.temp_dir / "node1")

    def test_save_load_with_children(self):
        root = BaseIntNode(value=10, directory=self.temp_dir / "root")
        child1 = BaseIntNode(value=20)
        child2 = BaseIntNode(value=30)
        root.add_child(child1, "child1")  # Specify dir_name for clarity
        root.add_child(child2, "child2")

        root.save_to_directory()

        loaded_root = TreeNode.load_from_directory(self.temp_dir / "root")

        self.assertEqual(len(loaded_root.children), 2)

        # Check children using dictionary keys (directory names):
        self.assertIn("child1", loaded_root.children)
        self.assertEqual(loaded_root.children["child1"].value, 20)

        self.assertIn("child2", loaded_root.children)
        self.assertEqual(loaded_root.children["child2"].value, 30)

    def test_load_missing_directory(self):
        loaded_node = TreeNode.load_from_directory(self.temp_dir / "nonexistent")
        self.assertIsNone(loaded_node)

    def test_children_property_no_directory(self):
        node = BaseIntNode(value=5)  # No directory
        self.assertEqual(len(node.children), 0)  # Should be empty

    def test_invalid_directory(self):
        with self.assertRaises(ValueError):
            node = BaseIntNode(value=7)
            node.save_to_directory()  # directory not specified

    def test_to_dict(self):
        node = BaseIntNode(value=15, directory=self.temp_dir / "node_to_dict", required_children={})
        expected_dict = {"node_type": "BaseIntNode", "required_children": {}, "value": 15}  # include required_children
        self.assertEqual(node.to_dict(), expected_dict)


if __name__ == '__main__':
    unittest.main()
