import json
import os
import unittest
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Any, Dict, Optional, List, Iterator, Mapping, Tuple
import shutil  # For directory cleanup
import tempfile  # For creating temporary directories

DATA_JSON = "node_data.json"


@dataclass(kw_only=True)  # Use kw_only=True here
class TreeNode(ABC):
    _node_registry = {}  # class registry - class variable

    directory: Optional[Path] = field(default=None, repr=False, compare=False)

    @classmethod
    def register_node_type(cls, node_type):  # decorator to register subclasses
        def decorator(subclass):
            cls._node_registry[node_type] = subclass
            return subclass

        return decorator

    @property  # children as a property
    def children(self) -> Mapping[str, 'TreeNode']:  # Return a dictionary
        children = {}
        if self.directory:
            for filename in os.listdir(self.directory):
                if os.path.isdir(os.path.join(self.directory, filename)):
                    child_path = os.path.join(self.directory, filename)
                    child_node = TreeNode.load_from_directory(child_path)
                    if child_node:
                        children[filename] = child_node  # Use filename as key

        return children

    def get_other_files_and_dirs(self) -> Iterator[Tuple[str, bool]]:
        if self.directory:
            for filename in os.listdir(self.directory):
                item_path = self.directory / filename  # Use Path for cleaner code
                if filename != DATA_JSON:
                    is_dir = item_path.is_dir()
                    if not is_dir or not (item_path / DATA_JSON).exists():  # Correct condition
                        yield filename, is_dir

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "node_type": self.node_type(),
        }

        for f in fields(self):
            if f.name not in ('directory'):
                # Handle potential JSON serialization issues (e.g., for custom objects):
                value = getattr(self, f.name)
                try:
                    json.dumps(value)  # Test if value is directly JSON serializable
                    data[f.name] = value
                except TypeError:  # Not directly serializable
                    data[f.name] = str(value)  # or a custom conversion method
        return data

    def save_to_directory(self, directory: Optional[str] = None):
        if directory:
            self.directory = Path(directory)
        if self.directory is None:
            raise ValueError("Directory must be specified")

        directory = str(self.directory)  # Convert Path to string for os.makedirs

        os.makedirs(directory, exist_ok=True)
        filepath = os.path.join(directory, DATA_JSON)  # save to "node_data.json" inside directory
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TreeNode':
        node_type = data.get("node_type")  # Use get() to handle missing node_type
        if not node_type or node_type not in cls._node_registry:  # Check that node_type is registered
            raise ValueError(f"Unknown or unregistered node type: {node_type}")
        node_class = cls._node_registry[node_type]
        kwargs = {k: v for k, v in data.items() if k not in ("node_type")}
        node = node_class(**kwargs)
        return node

    @classmethod
    def load_from_directory(cls, directory: str) -> Optional['TreeNode']:
        filepath = os.path.join(directory, DATA_JSON)  # load from  "node_data.json"
        if not os.path.exists(filepath):
            return None

        with open(filepath, "r") as f:
            data = json.load(f)
            node = cls.from_dict(data)
            node.directory = directory
            return node

    def add_child(self, child: 'TreeNode', dir_name: Optional[str] = None):
        if not isinstance(child, TreeNode):
            raise TypeError("Child must be an instance of TreeNode")

        if self.directory:
            child_dir = self.directory / (dir_name or child.node_type() + "_" + str(child))  # use dir_name if passed
            child.directory = child_dir
            child.save_to_directory(child_dir)
        else:
            raise ValueError("Cannot add a child without a directory set for the parent.")

    def remove_child(self, child_name):
        if self.directory and child_name in self.children:  # Check if dir is set and contains child
            child_dir = self.directory / child_name  # get child's directory path
            if child_dir.exists():  # Check if such directory exists
                shutil.rmtree(child_dir)  # remove directory
            else:
                raise FileNotFoundError  # Raise error if child's directory doesn't exist

    @abstractmethod
    def node_type(self) -> str:  # Type hint for return type
        pass

    @property
    @abstractmethod
    def valid(self) -> bool:
        pass

    def __str__(self) -> str:
        return f"{self.node_type()} Node"


@TreeNode.register_node_type('BaseIntNode')
@dataclass(kw_only=True)
class BaseIntNode(TreeNode):
    value: int  # Or any other data type you need

    def node_type(self) -> str:
        return "BaseIntNode"

    @property
    def valid(self) -> bool:  # Example validation
        return isinstance(self.value, int)

    def __str__(self) -> str:
        return f"Base Integer Node: {self.value}"


@TreeNode.register_node_type('NodeWithChildren')
@dataclass(kw_only=True)
class NodeWithChildren(TreeNode):
    required_children: Dict[str, str] = field(
        default_factory=lambda: {"child1": "BaseIntNode"})  # required child type and name

    def node_type(self) -> str:
        return 'NodeWithChildren'

    @property
    def valid(self) -> bool:
        if not self.directory:
            return False

        for child_name, child_type in self.required_children.items():  # iterate by name and type
            child = self.children.get(child_name)  # get child by name from children directory
            if not child or child.node_type() != child_type:  # Check both name and type
                return False
        return True


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

        loaded_parent = TreeNode.load_from_directory(parent_dir) #reload parent to refresh children
        self.assertTrue(loaded_parent.valid)  # Valid (correct child with correct name)




        # Test with wrong child name *in addition to* correct child
        child2 = BaseIntNode(value=2)
        parent.add_child(child2, "wrong_name")  # Correct type but wrong name
        loaded_parent = TreeNode.load_from_directory(parent_dir) #reload parent to refresh children

        self.assertTrue(loaded_parent.valid)  # Still valid (required child is present)



        child3 = NodeWithChildren(directory="child3")  # Incorrect type
        parent.add_child(child3, "child1")  # Correct name, wrong type

        loaded_parent = TreeNode.load_from_directory(parent_dir)  # reload to refresh children
        self.assertFalse(loaded_parent.valid)  # Invalid (wrong type)



        parent.remove_child("child1") # remove using new method

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
        node = BaseIntNode(value=15, directory=self.temp_dir / "node_to_dict")
        expected_dict = {"node_type": "BaseIntNode", "value": 15}
        self.assertEqual(node.to_dict(), expected_dict)


if __name__ == '__main__':
    unittest.main()
