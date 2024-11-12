import json
import os
import unittest
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Any, Dict, Optional, List, Iterator
import shutil  # For directory cleanup
import tempfile  # For creating temporary directories


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
    def children(self) -> List['TreeNode']:
        children = []  # create empty list for children if this is the first access to the property

        if self.directory:  # check if there is directory
            for filename in os.listdir(self.directory):
                if os.path.isdir(os.path.join(self.directory, filename)):
                    child_node = TreeNode.load_from_directory(os.path.join(self.directory, filename))
                    if child_node:
                        children.append(child_node)  # using the cached list
                        child_node.parent = self  # restore parent relationship
        return children

    # @property
    # def children(self) -> Iterator['TreeNode']: #return iterator
    #     if self.directory:
    #         for filename in os.listdir(self.directory):
    #             if os.path.isdir(os.path.join(self.directory, filename)):
    #                 child_node = TreeNode.load_from_directory(os.path.join(self.directory, filename))
    #                 if child_node:
    #                     yield child_node #yield loaded node

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
        filepath = os.path.join(directory, "node_data.json")  # save to "node_data.json" inside directory
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
        filepath = os.path.join(directory, "node_data.json")  # load from  "node_data.json"
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

    @abstractmethod
    def node_type(self) -> str:  # Type hint for return type
        pass

    def __str__(self) -> str:
        return f"{self.node_type()} Node"


@TreeNode.register_node_type('BaseIntNode')
@dataclass(kw_only=True)
class BaseIntNode(TreeNode):
    value: int  # Or any other data type you need

    def node_type(self) -> str:
        return "BaseIntNode"

    def __str__(self) -> str:
        return f"Base Integer Node: {self.value}"


class TestTreeNode(unittest.TestCase):
    def setUp(self):
        """Create a temporary directory for testing."""
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Clean up the temporary directory after each test."""
        shutil.rmtree(self.temp_dir)

    def test_save_load_single_node(self):
        node = BaseIntNode(value=42, directory=self.temp_dir / "node1")
        node.save_to_directory()

        loaded_node = TreeNode.load_from_directory(self.temp_dir / "node1")
        self.assertIsNotNone(loaded_node)
        self.assertEqual(loaded_node.value, 42)
        self.assertEqual(loaded_node.directory, self.temp_dir / "node1")

    def test_save_load_with_children(self):
        root = BaseIntNode(value=10, directory=self.temp_dir / "root")
        child1 = BaseIntNode(value=20)  # , directory=self.temp_dir / "root/child1") directory will be set during saving
        child2 = BaseIntNode(value=30)  # , directory=self.temp_dir / "root/child2")
        root.add_child(child1)
        root.add_child(child2)

        root.save_to_directory()

        loaded_root = TreeNode.load_from_directory(self.temp_dir / "root")

        self.assertEqual(len(loaded_root.children), 2)

        # Check children without relying on order:
        loaded_children_values = sorted([child.value for child in loaded_root.children])  # sort loaded values
        self.assertEqual(loaded_children_values, [20, 30])  # check sorted values

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
