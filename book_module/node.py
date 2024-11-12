import unittest
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass(kw_only=True)  # Use kw_only=True here
class TreeNode(ABC):
    parent: 'TreeNode' = field(default=None, repr=False) # repr=False to avoid recursion in repr
    children: list['TreeNode'] = field(default_factory=list, repr=False) #repr=False


    def add_child(self, child: 'TreeNode'):
        if not isinstance(child, TreeNode):
            raise TypeError("Child must be an instance of TreeNode")
        child.parent = self
        self.children.append(child)

    def remove_child(self, child: 'TreeNode'):
        if child in self.children:
            self.children.remove(child)
            child.parent = None

    @abstractmethod
    def node_type(self) -> str:  # Type hint for return type
        pass

    def __str__(self) -> str:
        return f"{self.node_type()} Node"

@dataclass(kw_only=True)
class BaseNode(TreeNode):
    data: int  # Or any other data type you need


    def node_type(self) -> str:
        return "Base"

    def __str__(self) -> str:
        return f"Base Node: {self.data}"


class TestTreeNode(unittest.TestCase):
    def test_add_child(self):
        root = BaseNode(data=5)
        data1 = BaseNode(data=10)
        root.add_child(data1)
        self.assertEqual(len(root.children), 1)
        self.assertEqual(root.children[0], data1)
        self.assertEqual(data1.parent, root)

    def test_remove_child(self):
        root = BaseNode(data=5)
        data1 = BaseNode(data=10)
        root.add_child(data1)
        root.remove_child(data1)
        self.assertEqual(len(root.children), 0)
        self.assertIsNone(data1.parent)

    def test_invalid_child_type(self):
        root = BaseNode(data=5)
        with self.assertRaises(TypeError):
            root.add_child("invalid child")  # Trying to add a string (not a TreeNode)


    def test_node_type(self):  # Test the abstract method
        root = BaseNode(data=5)
        data_node = BaseNode(data=15)
        self.assertEqual(root.node_type(), "Base")
        self.assertEqual(data_node.node_type(), "Base")

    def test_str_representation(self):  # Testing the __str__ method
        root = BaseNode(data=5)
        data_node = BaseNode(data=15)

        self.assertEqual(str(root), "Base Node: 5")
        self.assertEqual(str(data_node), "Base Node: 15")





if __name__ == '__main__':
    unittest.main()