# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import unittest
from gaevalidator.base import FieldBase, Validator


def error_msg(attr_name):
    return '%s has error' % attr_name


class FieldMock(FieldBase):
    def validate_field(self, value):
        if not value:
            return error_msg(self._attr)

    def transform_field(self, value):
        return int(value)


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


class FieldBaseTests(unittest.TestCase):
    def test_required(self):
        field_not_required = FieldBase()
        self.assertIsNone(None, field_not_required.validate(''))
        self.assertIsNone(field_not_required.validate(None))
        self.assertIsNone(field_not_required.validate('Foo'))
        field_required = FieldBase(required=True)
        self.assertIsNotNone(field_required.validate(''))
        self.assertIsNotNone(field_required.validate(None))
        self.assertIsNone(field_required.validate('Foo'))

    def test_default(self):
        DEFAULT = 'default'
        field = FieldBase(default=DEFAULT)
        self.assertEqual(DEFAULT, field.transform_field(''))
        self.assertEqual(DEFAULT, field.transform_field(None))
        self.assertEqual("X", field.transform_field('X'))

    def test_default_plus_required(self):
        DEFAULT = 'default'
        field = FieldBase(default=DEFAULT, required=True)
        self.assertEqual(DEFAULT, field.transform_field(''))
        self.assertEqual(DEFAULT, field.transform_field(None))
        self.assertEqual("X", field.transform_field('X'))
        self.assertIsNone(None, field.validate(''))
        self.assertIsNone(field.validate(None))