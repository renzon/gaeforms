# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import unittest
from gaevalidator.base import FieldBase, Validator


def error_msg(attr_name):
    return '%s has error' % attr_name


class FieldMock(FieldBase):
    def validate(self, value):
        if not value:
            return error_msg(self._attr)

    def transform(self,value):
        return int(value)

FAIL_PROTECTED_VALIDATION = 'fail protected'

mock1 = FieldMock()
mock2 = FieldMock()


class ValidatorExample(Validator):
    attr1 = mock1
    attr2 = mock2
    non_field = 'foo'



class ValidatorTests(unittest.TestCase):
    def test_fields(self):
        self.assertDictEqual({'attr1': mock1, 'attr2': mock2}, ValidatorExample._fields)

    def test_instance_values(self):
        v1 = ValidatorExample(attr1='a', attr2='b')
        v2 = ValidatorExample(attr1='c', attr2='d')
        self.assertTupleEqual(('a', 'b'), (v1.attr1, v1.attr2))
        self.assertTupleEqual(('c', 'd'), (v2.attr1, v2.attr2))


    def test_validate(self):
        v1 = ValidatorExample(attr1=True, attr2=True)
        self.assertDictEqual({}, v1.validate())
        v1 = ValidatorExample(attr1=False, attr2=True)
        self.assertDictEqual({'attr1': error_msg('attr1')}, v1.validate())
        v1 = ValidatorExample(attr1=True, attr2=False)
        self.assertDictEqual({'attr2': error_msg('attr2')}, v1.validate())
        v1 = ValidatorExample(attr1=False, attr2=False)
        self.assertDictEqual({'attr1': error_msg('attr1'), 'attr2': error_msg('attr2')}, v1.validate())

    def test_transform(self):
        v1 = ValidatorExample(attr1='1', attr2='2')
        self.assertDictEqual({'attr1': 1, 'attr2': 2}, v1.transform())
