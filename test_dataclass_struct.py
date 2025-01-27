"""
This is a unit test module for dataclass_struct.

Pylint doesn't see the methods injected by the dataclass_struct
decorator, so we disable related warnings below.
"""
# pylint: disable=no-member
# pylint: disable=R0903
# pylint: disable=C0115
# pylint: disable=C0116

# Disable false positive for dataclass lists
# pylint: disable=E1136

import unittest
import struct
from dataclasses import field, dataclass
from dataclass_struct import STRUCT_TYPE, ENCODING, dataclass_struct


@dataclass_struct
class SimpleTestModel:
    my_name: str = ''
    my_flt: float = field(default=0, metadata={STRUCT_TYPE: '<f'})
    my_num: int = field(default=0, metadata={STRUCT_TYPE: '<i'})
    no_struct: int = field(default=0, metadata={'dummy': '1'})


@dataclass_struct
@dataclass(order=True)
class ExplicitDataclass:
    my_name: str = ''
    my_flt: float = field(default=0, metadata={STRUCT_TYPE: '<f'})
    my_num: int = field(default=0, metadata={STRUCT_TYPE: '<i'})
    no_struct: int = field(default=0, metadata={'dummy': '1'})


@dataclass_struct
class StringTest:
    byte_name: bytes = field(default=b'', metadata={STRUCT_TYPE: '16s'})
    str_name: str = field(default='', metadata={STRUCT_TYPE: '16s'})
    str_with_enc: str = field(default='', metadata={STRUCT_TYPE: '32s',
                              ENCODING: 'utf-16'})


@dataclass_struct(use_encoding='ascii')
class DefaultEncodingTest:
    byte_name: bytes = field(default=b'', metadata={STRUCT_TYPE: '16s'})
    str_name: str = field(default='', metadata={STRUCT_TYPE: '16s'})
    str_with_enc: str = field(default='', metadata={STRUCT_TYPE: '32s',
                              ENCODING: 'utf-16'})


@dataclass_struct
class ListTest:
    float_list: [float] = field(default_factory=lambda: [],
                                metadata={STRUCT_TYPE: '<fff'})
    int_list: [int] = field(default=lambda: [],
                            metadata={STRUCT_TYPE: '<iiii'})


@dataclass_struct
class NestedDataclassStruct:
    first_num: int = field(default=0, metadata={STRUCT_TYPE: '<i'})
    nested_object: SimpleTestModel = field(default=SimpleTestModel())
    last_num: int = field(default=0, metadata={STRUCT_TYPE: 'i'})


@dataclass_struct
class DataclassListTest:
    my_num: int = field(default=0, metadata={STRUCT_TYPE: '<i'})
    dc_list: [SimpleTestModel] = field(default_factory=lambda: [])


class SimpleClassTestCase(unittest.TestCase):
    def test_testmodel(self):
        test_obj = SimpleTestModel('Name', 3.14, 42, 37)
        self.assertEqual('Name', test_obj.my_name)
        self.assertEqual(b'\xc3\xf5H@*\x00\x00\x00', test_obj.to_buffer())
        test_obj.my_num = 96
        self.assertEqual(b'\xc3\xf5H@`\x00\x00\x00', test_obj.to_buffer())
        test_obj = SimpleTestModel()
        self.assertEqual(test_obj.my_flt, 0)
        test_obj.from_buffer(b'\xc3\xf5H@*\x00\x00\x00')
        self.assertAlmostEqual(test_obj.my_flt, 3.14, 5)

        test_obj = SimpleTestModel.instance_from_buffer(
            b'\xc3\xf5H@`\x00\x00\x00')
        self.assertAlmostEqual(test_obj.my_flt, 3.14, 5)

    def test_explicit_dataclass(self):
        test_obj = ExplicitDataclass('Name', 3.14, 42, 37)
        self.assertEqual('Name', test_obj.my_name)
        self.assertEqual(b'\xc3\xf5H@*\x00\x00\x00', test_obj.to_buffer())
        test_obj.my_num = 96
        self.assertEqual(b'\xc3\xf5H@`\x00\x00\x00', test_obj.to_buffer())
        test_obj = ExplicitDataclass()
        self.assertEqual(test_obj.my_flt, 0)
        test_obj.from_buffer(b'\xc3\xf5H@*\x00\x00\x00')
        self.assertAlmostEqual(test_obj.my_flt, 3.14, 5)

        test_obj = ExplicitDataclass.instance_from_buffer(
            b'\xc3\xf5H@`\x00\x00\x00')
        self.assertAlmostEqual(test_obj.my_flt, 3.14, 5)

    def test_basic_string(self):
        buff = b'Hello World\x00\x00\x00\x00\x00Bye bye\x00\x00\x00'\
            b'\x00\x00\x00\x00\x00\x00\xff\xfea\x00n\x00o\x00t\x00h'\
            b'\x00e\x00r\x00 \x00o\x00n\x00e\x00\x00\x00\x00\x00\x00'\
            b'\x00\x00\x00'
        test_obj = StringTest(b'Hello World', 'Bye bye', 'another one')
        self.assertEqual(buff, test_obj.to_buffer())
        new_instance = StringTest.instance_from_buffer(buff)
        self.assertEqual(new_instance.byte_name,
                         b'Hello World\x00\x00\x00\x00\x00')
        self.assertEqual(new_instance.str_name, 'Bye bye')
        self.assertEqual(new_instance.str_with_enc, 'another one')

    def test_default_encoding(self):
        buff = b'Hello World\x00\x00\x00\x00\x00Bye bye\x00\x00\x00'\
            b'\x00\x00\x00\x00\x00\x00\xff\xfea\x00n\x00o\x00t\x00h'\
            b'\x00e\x00r\x00 \x00o\x00n\x00e\x00\x00\x00\x00\x00\x00'\
            b'\x00\x00\x00'
        test_obj = DefaultEncodingTest(b'Hello World', 'Bye bye',
                                       'another one')
        self.assertEqual(buff, test_obj.to_buffer())
        new_instance = DefaultEncodingTest.instance_from_buffer(buff)
        self.assertEqual(new_instance.byte_name,
                         b'Hello World\x00\x00\x00\x00\x00')
        self.assertEqual(new_instance.str_name, 'Bye bye')
        self.assertEqual(new_instance.str_with_enc, 'another one')

    def test_basic_list(self):
        buff = b'\xcd\xcc\x8c?\x00\x00\x80?33\xf3@\x01\x00\x00\x00\x02\x00'\
            b'\x00\x00\x03\x00\x00\x00\x04\x00\x00\x00'
        test_obj = ListTest([1.1, 1.0, 7.6], [1, 2, 3, 4])
        self.assertEqual(buff, test_obj.to_buffer())
        self.assertAlmostEqual(test_obj.float_list[0], 1.1, 5)
        test_obj = ListTest([1.1, 1.0, 7.6, 7.7], [1, 2, 3, 4])
        self.assertRaises(struct.error, test_obj.to_buffer)
        test_obj = ListTest([1.1, 1.0], [1, 2, 3, 4])
        self.assertRaises(struct.error, test_obj.to_buffer)
        new_instance = ListTest.instance_from_buffer(buff)
        self.assertAlmostEqual(new_instance.float_list[0], 1.1, 5)
        self.assertAlmostEqual(new_instance.float_list[1], 1.0, 5)

    def test_nested_instance(self):
        buffer = b'\x01\x00\x00\x00\xc3\xf5H@\x02\x00\x00\x00\x02\x00\x00\x00'
        test_obj = NestedDataclassStruct(1, SimpleTestModel('', 3.14, 2, 0), 2)
        self.assertEqual(buffer, test_obj.to_buffer())
        self.assertEqual(test_obj.first_num, 1)
        self.assertEqual(test_obj.nested_object.my_num, 2)
        self.assertEqual(test_obj.last_num, 2)
        newobj = NestedDataclassStruct.instance_from_buffer(buffer)
        self.assertEqual(newobj.first_num, 1)
        self.assertEqual(newobj.nested_object.my_num, 2)
        self.assertEqual(newobj.last_num, 2)

    def test_list_dataclass(self):
        buffer = b'\x02\x00\x00\x00\xc3\xf5H@\x01\x00\x00\x00\xc3\xf5H@\x02'\
            b'\x00\x00\x00\xc3\xf5H@\x03\x00\x00\x00'
        test_obj = DataclassListTest(2, [
            SimpleTestModel('Name', 3.14, 1, 42),
            SimpleTestModel('Name', 3.14, 2, 42),
            SimpleTestModel('Name', 3.14, 3, 42)])
        self.assertEqual(buffer, test_obj.to_buffer())
        newobj = DataclassListTest.instance_from_buffer(buffer)
        self.assertEqual(newobj.my_num, 2)
        self.assertEqual(len(newobj.dc_list), 0)
        newobj.dc_list = [
            SimpleTestModel(),
            SimpleTestModel(),
            SimpleTestModel()]
        newobj.from_buffer(buffer)
        self.assertEqual(newobj.my_num, 2)
        self.assertEqual(newobj.dc_list[0].my_num, 1)
        self.assertEqual(newobj.dc_list[1].my_num, 2)
        self.assertEqual(newobj.dc_list[2].my_num, 3)


if __name__ == '__main__':
    unittest.main()
