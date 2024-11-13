import unittest
import unittest
from datetime import datetime
from dataclasses import dataclass, fields

from book_module.node import serialize_value, deserialize_value, TreeNode

@TreeNode.register_node_type('TestDataClass')
@dataclass
class TestDataClassNode(TreeNode):
    name: str
    value: int
    def node_type(self) -> str:
         return "TestDataClass"

def serialize_test_object(obj):
    return {f.name: serialize_value(getattr(obj, f.name)) for f in fields(obj) if f.name not in ('directory', 'required_children')}

class TestSerialization(unittest.TestCase):

    def test_serialize_datetime(self):
        now = datetime.now()
        serialized = serialize_value(now)
        self.assertEqual(serialized, now.isoformat())

    def test_serialize_dataclass(self):
        data = TestDataClassNode(name="test", value=123)
        serialized = serialize_test_object(data)  # Use the helper function
        self.assertEqual(serialized, {'name': 'test', 'value': 123})

    def test_serialize_other_types(self):
        self.assertEqual(serialize_value(123), 123)
        self.assertEqual(serialize_value("test"), "test")
        self.assertEqual(serialize_value([1, 2, 3]), [1, 2, 3])
        test_dict = {"a": 1, "b": "2"}
        self.assertEqual(serialize_value(test_dict), test_dict)


    def test_deserialize_datetime(self):
        now = datetime.now()
        now_str = now.isoformat()
        deserialized = deserialize_value(now_str)
        self.assertEqual(deserialized, now)

    def test_deserialize_invalid_datetime(self):
        invalid_datetime_str = "not a datetime string"
        deserialized = deserialize_value(invalid_datetime_str)
        self.assertEqual(deserialized, invalid_datetime_str) # should return the same value it received


    def test_deserialize_dataclass(self): #check if we properly deserialize existing dataclass
        data_dict = {'node_type': 'TestDataClass', 'name': 'test', 'value': 123}
        @TreeNode.register_node_type('TestDataClass') #register before using it
        @dataclass
        class TestDataClassNode(TreeNode):
            name: str
            value: int

            def node_type(self):
                return "TestDataClass"
        deserialized = deserialize_value(data_dict)
        self.assertEqual(deserialized.name, "test")
        self.assertEqual(deserialized.value, 123)

    def test_deserialize_other_types(self):
        self.assertEqual(deserialize_value(123), 123)
        self.assertEqual(deserialize_value("test"), "test")
        self.assertEqual(deserialize_value([1, 2, 3]), [1, 2, 3])
        test_dict = {"a": 1, "b": "2"}
        self.assertEqual(deserialize_value(test_dict), test_dict)


if __name__ == '__main__':
    unittest.main()
