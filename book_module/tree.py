from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Mapping, cast
from .node import TreeNode

@dataclass
class Tree:
    root: Optional[TreeNode] = None
    _current_node: Optional[TreeNode] = field(init=False, default=None)

    def create_root(self, node_type: str, directory: str, **kwargs) -> TreeNode:
        if self.root:
            raise ValueError("Root node already exists.")

        if node_type not in TreeNode._node_registry:
            raise ValueError(f"Unknown node type: {node_type}")

        node_class = TreeNode._node_registry[node_type]
        self.root = node_class(directory=directory, **kwargs)
        self._current_node = self.root
        self.root.save_to_directory()
        return self.root

    def navigate_to(self, child_name: str) -> Optional[TreeNode]:
        if not self._current_node:
            return None  # Or raise exception: raise ValueError("Current node is not set.")

        if child_name in self._current_node.children:
            self._current_node = self._current_node.children[child_name]
            return self._current_node
        return None

    def add_child(self, node_type: str, dir_name: Optional[str] = None, **kwargs) -> Optional[TreeNode]:
        if not self._current_node:
            return None  # Or raise exception

        if node_type not in TreeNode._node_registry:
            raise ValueError(f"Unknown node type: {node_type}")

        node_class = TreeNode._node_registry[node_type]
        child_node = node_class(**kwargs)
        self._current_node.add_child(child_node, dir_name)
        return child_node

    @property
    def current_node(self) -> Optional[TreeNode]:
        return self._current_node

    def reset_to_root(self):
        self._current_node = self.root

    def load_from_directory(self, directory: str) -> bool:
        loaded_root = TreeNode.load_from_directory(directory)
        if loaded_root:
            self.root = loaded_root
            self._current_node = self.root
            return True
        return False