import unittest
from dataclasses import field, dataclass
from dataclass_struct import struct_type, dataclass_struct


@dataclass_struct
class TestModel:
    my_name: str = ''
    my_flt: float = field(default=0, metadata={struct_type: '<f'})
    my_num: int = field(default=0, metadata={struct_type: '<i'})
    no_struct: int = field(default=0, metadata={'dummy': '1'})

@dataclass_struct
@dataclass(order=True)
class ExplicitDataclass:
    my_name: str = ''
    my_flt: float = field(default=0, metadata={struct_type: '<f'})
    my_num: int = field(default=0, metadata={struct_type: '<i'})
    no_struct: int = field(default=0, metadata={'dummy': '1'})

@dataclass_struct
class StringTest:
    byte_name: bytes = field(default=b'', metadata={struct_type: '16s'})
    str_name: str = field(default='', metadata={struct_type: '16s'})
    

class SimpleClassTestCase(unittest.TestCase):
    def test_testmodel(self):
        test_obj = TestModel('Name', 3.14, 42,37)
        self.assertEqual('Name', test_obj.my_name)
        self.assertEqual(b'\xc3\xf5H@*\x00\x00\x00', test_obj.to_buffer())
        test_obj.my_num = 96
        self.assertEqual(b'\xc3\xf5H@`\x00\x00\x00', test_obj.to_buffer())
        test_obj = TestModel()
        self.assertEqual(test_obj.my_flt, 0)
        test_obj.from_buffer(b'\xc3\xf5H@*\x00\x00\x00')
        self.assertAlmostEqual(test_obj.my_flt, 3.14, 5)

        test_obj = TestModel.instance_from_buffer(b'\xc3\xf5H@`\x00\x00\x00')
        self.assertAlmostEqual(test_obj.my_flt, 3.14, 5)

    def test_explicit_dataclass(self):
        test_obj = ExplicitDataclass('Name', 3.14, 42,37)
        self.assertEqual('Name', test_obj.my_name)
        self.assertEqual(b'\xc3\xf5H@*\x00\x00\x00', test_obj.to_buffer())
        test_obj.my_num = 96
        self.assertEqual(b'\xc3\xf5H@`\x00\x00\x00', test_obj.to_buffer())
        test_obj = ExplicitDataclass()
        self.assertEqual(test_obj.my_flt, 0)
        test_obj.from_buffer(b'\xc3\xf5H@*\x00\x00\x00')
        self.assertAlmostEqual(test_obj.my_flt, 3.14, 5)

        test_obj = ExplicitDataclass.instance_from_buffer(b'\xc3\xf5H@`\x00\x00\x00')
        self.assertAlmostEqual(test_obj.my_flt, 3.14, 5)

    def test_string(self):
        test_obj = StringTest(b'Hello World', 'Bye bye')
        self.assertEqual(b'Hello World\x00\x00\x00\x00\x00Bye bye\x00\x00\x00\x00\x00\x00\x00\x00\x00', test_obj.to_buffer())
        new_instance = StringTest.instance_from_buffer(b'Hello World\x00\x00\x00\x00\x00Bye !!!\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        self.assertEqual(new_instance.byte_name, b'Hello World\x00\x00\x00\x00\x00')
        self.assertEqual(new_instance.str_name, 'Bye !!!\x00\x00\x00\x00\x00\x00\x00\x00\x00')

if __name__ == '__main__':
    unittest.main()
