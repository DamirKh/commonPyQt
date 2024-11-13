import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, fields, is_dataclass
from pathlib import Path
from typing import Any, Dict, Optional, List, Iterator, Mapping, Tuple
import shutil  # For directory cleanup
from datetime import datetime

NODE_TYPE = "node_type"
DATA_JSON = "node_data.json"


# Helper function to handle datetime serialization
def serialize_value(value):
    if isinstance(value, datetime):
        return value.isoformat()
    elif isinstance(value, dict):  # handle dictionaries, to prevent recursive serialization for dataclass
        return value
    elif is_dataclass(value):
        return value.to_dict()
    return value


def deserialize_value(value):
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return value
    elif isinstance(value, dict):
        if NODE_TYPE in value and value[NODE_TYPE] in TreeNode._node_registry:
            node_class = TreeNode._node_registry[value[NODE_TYPE]]
            # Create dataclass instance:
            try:
                return node_class(**{f.name: deserialize_value(value.get(f.name)) for f in fields(node_class)})
            except Exception as e:  # better to catch TypeError but other exceptions can occure during class construction
                print(f"Error creating dataclass instance: {e}")  # debugging
                return value  # if for some reason construction failed - return dict unchanged

        return value  # Regular dictionary, return as is
    return value


@dataclass(kw_only=True)  # Use kw_only=True here
class TreeNode(ABC):
    _node_registry = {}  # class registry - class variable

    directory: Optional[Path] = field(default=None, repr=False, compare=False)
    required_children: Dict[str, str] = field(default_factory=dict)

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
            NODE_TYPE: self.node_type()
        }
        for f in fields(self):
            if f.name not in ('directory',):
                value = getattr(self, f.name)
                data[f.name] = serialize_value(value)  # Serialize value if needed
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
        node_type = data.get(NODE_TYPE)  # Use get() to handle missing node_type
        if not node_type or node_type not in cls._node_registry:  # Check that node_type is registered
            raise ValueError(f"Unknown or unregistered node type: {node_type}")
        node_class = cls._node_registry[node_type]
        kwargs = {k: deserialize_value(v) for k, v in data.items() if k not in (NODE_TYPE,)}
        # kwargs = {k: v for k, v in data.items() if k not in ("node_type")}
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
            node.directory = Path(directory)  # Convert to Path HERE!
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

    def node_type(self) -> str:
        return type(self).__name__

    @property
    def valid(self) -> bool:
        """
        Checks if the node is valid, including required children checks.
        Subclasses can override this method to add their own validation logic.
        Make sure to call `super().valid()` in subclasses to include
        the required children validation.
        """
        if not self.directory:
            return False

        for child_name, child_type in self.required_children.items():  # iterate by name and type
            child = self.children.get(child_name)  # get child by name from children directory
            if not child or child.node_type() != child_type:  # Check both name and type
                return False
        return True

    def __str__(self) -> str:
        return f"{self.node_type()} Node"


@TreeNode.register_node_type('BaseIntNode')
@dataclass(kw_only=True)
class BaseIntNode(TreeNode):
    """This class is mainly for run tests"""
    value: int  # Or any other data type you need

    @property
    def valid(self) -> bool:
        is_value_valid = isinstance(self.value, int)  # Perform BaseIntNode-specific check

        # Call super().valid() AFTER your specific checks. This way you can return False early.
        return is_value_valid and super().valid  # call general valid method

    def __str__(self) -> str:
        return f"Base Integer Node: {self.value}"


@TreeNode.register_node_type('NodeWithChildren')
@dataclass(kw_only=True)
class NodeWithChildren(TreeNode):
    """This class is mainly for run tests"""
    required_children: Dict[str, str] = field(
        default_factory=lambda: {"child1": "BaseIntNode"})  # required child type and name

    @property
    def valid(self) -> bool:
        return super().valid  # just call TreeNode general validation
