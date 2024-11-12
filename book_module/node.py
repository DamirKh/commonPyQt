from abc import ABC, abstractmethod

class TreeNode(ABC):
    def __init__(self, parent=None):
        self.parent = parent
        self.children = []

    def add_child(self, child):
        if not isinstance(child, TreeNode):
            raise TypeError("Child must be an instance of TreeNode")
        child.parent = self
        self.children.append(child)

    def remove_child(self, child):
        if child in self.children:
            self.children.remove(child)
            child.parent = None

    @abstractmethod
    def node_type(self):
        pass

    def __str__(self):  # Basic string representation for debugging
        return f"{self.node_type()} Node"


class DataNode(TreeNode):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data

    def node_type(self):
        return "Data"

    def __str__(self):
        return f"Data Node: {self.data}"


class CalculationNode(TreeNode):
    def __init__(self, operation, parent=None):
        super().__init__(parent)
        self.operation = operation  # e.g., "+", "-", "*", "/"

    def node_type(self):
        return "Calculation"

    def __str__(self):
        return f"Calculation Node: {self.operation}"


if __name__ == '__main__':
    # Example Usage:

    root = CalculationNode("+")
    data1 = DataNode(10)
    data2 = DataNode(20)

    root.add_child(data1)
    root.add_child(data2)

    calc_node = CalculationNode("*")
    data3 = DataNode(5)
    calc_node.add_child(data3)

    root.add_child(calc_node)


    # Traversal (example - depth-first)
    def print_tree(node, level=0):
        print("  " * level + str(node))
        for child in node.children:
            print_tree(child, level + 1)


    print_tree(root)
