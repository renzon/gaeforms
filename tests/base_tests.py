# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import datetime
import unittest
from decimal import Decimal

from google.appengine.ext.ndb import Model, Key

from gaeforms import base, settings
from gaeforms.base import BaseField, Form, IntegerField, DecimalField, StringField, DateField, DateTimeField, \
    FloatField, EmailField, BooleanField, KeyField
from util import GAETestCase

@settings.locale_factory
def locale_stub():
    return 'en_us'
@settings.tz_factory
def timezone_stub():
    return 'America/Sao_Paulo'


def error_msg(attr_name):
    return '%s has error' % attr_name


class MockField(BaseField):
    def validate_field(self, value):
        if not value:
            return error_msg(self._attr)

    def normalize_field(self, value):
        return int(value)

    def localize_field(self, value):
        return {1: 'one', 2: 'two'}.get(value)


mock1 = MockField()
mock2 = MockField()


class FormExample(Form):
    attr1 = mock1
    attr2 = mock2
    non_field = 'foo'


class FormTests(unittest.TestCase):
    def test_fields(self):
        self.assertDictEqual({'attr1': mock1, 'attr2': mock2}, FormExample._fields)

    def test_instance_values(self):
        form = FormExample(attr1='a', attr2='b')
        v2 = FormExample(attr1='c', attr2='d')
        self.assertTupleEqual(('a', 'b'), (form.attr1, form.attr2))
        self.assertTupleEqual(('c', 'd'), (v2.attr1, v2.attr2))

    def test_validate(self):
        form = FormExample(attr1=True, attr2=True)
        self.assertDictEqual({}, form.validate())
        form = FormExample(attr1=False, attr2=True)
        self.assertDictEqual({'attr1': error_msg('attr1')}, form.validate())
        form = FormExample(attr1=True, attr2=False)
        self.assertDictEqual({'attr2': error_msg('attr2')}, form.validate())
        form = FormExample(attr1=False, attr2=False)
        self.assertDictEqual({'attr1': error_msg('attr1'), 'attr2': error_msg('attr2')}, form.validate())

    def test_normalize(self):
        form = FormExample(attr1='1', attr2='2')
        self.assertDictEqual({'attr1': 1, 'attr2': 2}, form.normalize())

    def test_normalize(self):
        form = FormExample(attr1='1', attr2='2')
        self.assertDictEqual({'attr1': 1, 'attr2': 2}, form.normalize())

    def test_localize(self):
        form = FormExample()
        self.assertFalse(hasattr(form, 'attr1'))
        self.assertFalse(hasattr(form, 'attr2'))
        self.assertDictEqual({'attr1': 'one', 'attr2': 'two'}, form.localize(attr1=1, attr2=2))
        self.assertDictEqual({'attr1': 'one', 'attr2': 'two'}, {'attr1': form.attr1, 'attr2': form.attr2})

    def test_localize_with_explicity_fields(self):
        form = FormExample()
        self.assertFalse(hasattr(form, 'attr1'))
        self.assertFalse(hasattr(form, 'attr2'))
        self.assertDictEqual({'attr1': 'one'}, form.localize('attr1', attr1=1, attr2=2))
        self.assertDictEqual({'attr2': 'two'}, form.localize('attr2', attr1=1, attr2=2))
        self.assertDictEqual({'attr1': 'one', 'attr2': 'two'}, form.localize('attr1', 'attr2', attr1=1, attr2=2))

    def test_fill(self):
        form = FormExample()
        self.assertFalse(hasattr(form, 'attr1'))
        self.assertFalse(hasattr(form, 'attr2'))
        form.fill(attr1='one', attr2='two')
        self.assertDictEqual({'attr1': 'one', 'attr2': 'two'}, {'attr1': form.attr1, 'attr2': form.attr2})


class BaseFieldTests(unittest.TestCase):
    def test_required(self):
        field_not_required = BaseField()

        self.assertIsNone(None, field_not_required.validate(''))
        self.assertIsNone(field_not_required.validate(None))
        self.assertIsNone(field_not_required.validate('Foo'))
        field_required = BaseField(required=True)
        field_required._attr = 'req'
        self.assertEqual('Required field', field_required.validate(''))
        self.assertEqual('Required field', field_required.validate(None))
        self.assertIsNone(field_required.validate('Foo'))

    def test_default(self):
        DEFAULT = 'default'
        field = BaseField(default=DEFAULT)
        self.assertEqual(DEFAULT, field.normalize(''))
        self.assertEqual(DEFAULT, field.normalize(None))
        self.assertEqual("X", field.normalize('X'))

    def test_default_plus_required(self):
        DEFAULT = 'default'
        field = BaseField(default=DEFAULT, required=True)
        self.assertEqual(DEFAULT, field.normalize(''))
        self.assertEqual(DEFAULT, field.normalize(None))
        self.assertEqual("X", field.normalize('X'))
        self.assertIsNone(None, field.validate(''))
        self.assertIsNone(field.validate(None))
        self.assertIsNone(field.validate('X'))

    def test_choices(self):
        field = BaseField(choices=['1', '2'])
        field._attr = 'foo'
        self.assertIsNone(field.validate('1'))
        self.assertIsNone(field.validate('2'))
        self.assertEqual('Must be one of: 1; 2', field.validate(None))

    def test_repeated(self):
        field = BaseField(repeated=True)
        self.assertIsNone(field.validate([]))
        self.assertIsNone(field.validate(['1']))
        self.assertIsNone(field.validate(['1', '2']))
        self.assertIsNone(field.validate(None))
        self.assertIsNone(field.validate([None]))

    def test_repeated_plus_required(self):
        field = BaseField(repeated=True, required=True)
        field._attr = 'req'

        self.assertIsNone(field.validate(['1']))
        self.assertIsNone(field.validate(['1', '2']))
        self.assertEqual('Required field', field.validate(None))
        self.assertEqual('Required field', field.validate([None]))
        self.assertEqual('Required field', field.validate([]))
        self.assertEqual('Required field', field.validate(['1,', None]))

    def test_repeated_normalization(self):
        field = MockField(repeated=True)
        self.assertListEqual([1, 2, 3], field.normalize(['1', '2', '3']))


class EmailFieldTests(unittest.TestCase):
    def test_validate(self):
        field = EmailField()
        field._attr = 'contact_email'

        self.assertEqual('Invalid email', field.validate('aa'))
        self.assertEqual('Invalid email', field.validate('a@'))
        self.assertEqual('Invalid email', field.validate('a@com'))
        self.assertIsNone(field.validate('a@google.com'))


class BooleanFieldTests(unittest.TestCase):
    def test_normalization(self):
        field = BooleanField()
        self.assertIsNone(field.normalize(None))
        self.assertIsNone(field.normalize(''))
        self.assertTrue(field.normalize('true'))
        self.assertTrue(field.normalize('True'))
        self.assertTrue(field.normalize(True))
        self.assertTrue(field.normalize('TRUE'))
        self.assertFalse(field.normalize('false'))
        self.assertFalse(field.normalize('False'))
        self.assertFalse(field.normalize(False))
        self.assertFalse(field.normalize('FALSE'))

    def test_validation(self):
        field = BooleanField()
        field._set_attr_name('n')
        self.assertIsNone(field.validate(None))
        self.assertIsNone(field.validate(''))
        self.assertIsNone(field.validate('true'))
        self.assertIsNone(field.validate('True'))
        self.assertIsNone(field.validate('TRUE'))
        self.assertIsNone(field.validate(True))
        self.assertIsNone(field.validate('False'))
        self.assertIsNone(field.validate(False))
        self.assertIsNone(field.validate('false'))
        self.assertIsNone(field.validate('false'))
        self.assertIsNone(field.validate('FALSE'))
        self.assertEqual('Must be true or false', field.validate('foo'))
        self.assertEqual('Must be true or false', field.validate('not false'))
        self.assertEqual('Must be true or false', field.validate('not true'))

    def test_localization(self):
        field = BooleanField()
        field._set_attr_name('n')
        self.assertTrue(field.localize(True))
        self.assertFalse(field.localize(False))


class KeyFieldTests(GAETestCase):
    def test_normalization_without_kind(self):
        class ModelMock(Model):
            pass

        key = Key(ModelMock, 1)
        model_mock = ModelMock()
        model_mock.put()
        field = KeyField()
        self.assertIsNone(field.normalize(None))
        self.assertIsNone(field.normalize(''))
        self.assertEqual(model_mock.key, field.normalize(model_mock))
        self.assertEqual(key, field.normalize(key))
        self.assertEqual(key, field.normalize(key.urlsafe()))
        self.assertRaises(Exception, field.normalize, '1')
        self.assertRaises(Exception, field.normalize, 'abcd')

    def test_normalization_wit_kind(self):
        class ModelMock(Model):
            pass

        key = Key(ModelMock, 1)

        field = KeyField(ModelMock)
        self.assertIsNone(field.normalize(None))
        self.assertIsNone(field.normalize(''))
        self.assertEqual(key, field.normalize(key))
        self.assertEqual(key, field.normalize(key.urlsafe()))
        self.assertEqual(key, field.normalize('1'))
        self.assertRaises(Exception, field.normalize, 'abcd')

    def test_validation_without_kind(self):
        class ModelMock(Model):
            pass

        key = Key(ModelMock, 1)

        field = KeyField()
        self.assertIsNone(field.validate(None))
        self.assertIsNone(field.validate(''))
        self.assertIsNone(field.validate(key))
        self.assertIsNone(field.validate(key.urlsafe()))
        self.assertEqual("Key's kind should be defined", field.validate('1'))
        self.assertEqual('Invalid key', field.validate('abcd'))

    def test_validation_with_kind(self):
        class ModelMock(Model):
            pass

        key = Key(ModelMock, 1)

        field = KeyField(ModelMock)
        self.assertIsNone(field.validate(None))
        self.assertIsNone(field.validate(''))
        self.assertIsNone(field.validate(key))
        self.assertIsNone(field.validate(key.urlsafe()))
        self.assertIsNone(field.validate('1'))
        self.assertEqual('Invalid key', field.validate('abcd'))

    def test_localization(self):
        class ModelMock(Model):
            pass

        key = Key(ModelMock, 1)
        field = KeyField()
        field._set_attr_name('n')
        self.assertEqual(1, field.localize(key))


class IntergerFieldTests(unittest.TestCase):
    def test_normalization(self):
        field = IntegerField()
        self.assertIsNone(field.normalize(None))
        self.assertIsNone(field.normalize(''))
        self.assertEqual(0, field.normalize('0'))
        self.assertEqual(1, field.normalize(1))
        self.assertEqual(0, field.normalize('0.0'))
        self.assertEqual(1000, field.normalize('1,000.0'))
        self.assertEqual(1111000, field.normalize('1,111,000.0'))
        self.assertEqual(1, field.normalize('1'))

    def test_default(self):
        field = IntegerField(default=1)
        self.assertEqual(1, field.normalize(None))
        self.assertEqual(1, field.normalize(''))
        self.assertEqual(0, field.normalize('0'))
        self.assertEqual(0, field.normalize('0.0'))
        self.assertEqual(1000, field.normalize('1,000.0'))
        self.assertEqual(1111000, field.normalize('1,111,000.0'))
        self.assertEqual(1, field.normalize('1'))

    def test_validation(self):
        field = IntegerField()
        field._set_attr_name('n')
        self.assertIsNone(field.validate(None))
        self.assertIsNone(field.validate(''))
        self.assertIsNone(field.validate('0'))
        self.assertIsNone(field.validate('1'))
        self.assertIsNone(field.validate(1))
        self.assertEqual('Must be integer', field.validate('foo'))
        self.assertEqual('Must be integer', field.validate('123h'))
        self.assertEqual('Must be integer', field.validate('0x456'))

    def test_validation_lower(self):
        field = IntegerField(lower=1)
        field._set_attr_name('n')
        self.assertIsNone(field.validate('1'))
        self.assertEqual('Must be greater than 1', field.validate('0'))

    def test_validation_upper(self):
        field = IntegerField(upper=1)
        field._set_attr_name('n')
        self.assertIsNone(field.validate('1'))
        self.assertEqual('Must be less than 1', field.validate('2'))

    def test_repeated_localization(self):
        field = IntegerField(repeated=True)
        self.assertListEqual([1000, 2222222, 3], field.localize([1000, 2222222, 3]))
        self.assertListEqual([''], field.localize([None]))

    def test_zero(self):
        field = IntegerField()
        self.assertEqual(0, field.localize(0))


class FloatFieldTests(unittest.TestCase):
    def test_zero(self):
        field = FloatField()
        self.assertEqual('0', field.localize(0.0))
        self.assertEqual('0', field.localize(0))

    def test_normalization(self):
        field = FloatField()
        self.assertIsNone(field.normalize(None))
        self.assertIsNone(field.normalize(''))
        self.assertAlmostEqual(1.339999999, field.normalize('1.339999999'))
        self.assertAlmostEqual(0, field.normalize('0'))
        self.assertAlmostEqual(1, field.normalize(1))
        self.assertAlmostEqual(1.34, field.normalize('1.34'))
        self.assertAlmostEqual(1.34, field.normalize(1.34))
        self.assertAlmostEqual(1000.34, field.normalize('1,000.34'))
        self.assertAlmostEqual(1111000.34, field.normalize('1,111,000.34'))
        self.assertAlmostEqual(1111000.3399999, field.normalize('1,111,000.3399999'))

    def test_localization(self):
        field = FloatField()
        self.assertAlmostEqual('', field.localize(None))
        self.assertAlmostEqual('', field.localize(''))
        self.assertAlmostEqual('1.34', field.localize(1.34))
        self.assertAlmostEqual('1,111,000.34', field.localize(1111000.34))
        self.assertAlmostEqual('1,111,000.33', field.localize(1111000.33))

    def test_validation(self):
        field = FloatField()
        field._set_attr_name('n')
        self.assertIsNone(field.validate(None))
        self.assertIsNone(field.validate(''))
        self.assertIsNone(field.validate('0'))
        self.assertIsNone(field.validate('1'))
        self.assertIsNone(field.validate(1))
        self.assertIsNone(field.validate(1.34))
        self.assertIsNone(field.validate('1,090,898.00'))
        self.assertEqual('Must be a number', field.validate('foo'))
        self.assertEqual('Must be a number', field.validate('123h'))
        self.assertEqual('Must be a number', field.validate('0x456'))

    def test_validation_lower(self):
        field = FloatField(lower=1.2)
        field._set_attr_name('n')
        self.assertIsNone(field.validate('1.21'))
        self.assertEqual('Must be greater than 1.2', field.validate('0'))

    def test_validation_upper(self):
        field = FloatField(upper=1.3)
        field._set_attr_name('n')
        self.assertIsNone(field.validate('1.29'))
        self.assertEqual('Must be less than 1.3', field.validate('2'))


class DecimalFieldTests(unittest.TestCase):
    def test_zero(self):
        field = DecimalField()
        self.assertEqual('0', field.localize(Decimal('0.0')))
        self.assertEqual('0', field.localize(Decimal('0')))

    def test_normalization(self):
        field = DecimalField()
        self.assertIsNone(field.normalize(None))
        self.assertIsNone(field.normalize(''))
        self.assertEqual(Decimal('1.34'), field.normalize('1.339999999'))
        self.assertEqual(Decimal('0.00'), field.normalize('0'))
        self.assertEqual(Decimal('1.34'), field.normalize('1.34'))
        self.assertEqual(Decimal('1.34'), field.normalize(Decimal('1.34')))
        self.assertEqual(Decimal('1000.34'), field.normalize('1,000.34'))
        self.assertEqual(Decimal('1111000.34'), field.normalize('1,111,000.34'))
        self.assertEqual(Decimal('1111000.34'), field.normalize('1,111,000.3399999'))
        field = DecimalField(decimal_places=3)
        self.assertEqual(Decimal('1.340'), field.normalize('1.339999999'))

    def test_localization(self):
        field = DecimalField()
        self.assertEqual('', field.localize(None))
        self.assertEqual('', field.localize(''))
        self.assertEqual('1.34', field.localize(Decimal('1.34')))
        self.assertEqual('1,111,000.34', field.localize(Decimal('1111000.34')))
        self.assertEqual('1,111,000.33', field.localize(Decimal('1111000.33')))

    def test_validation(self):
        field = DecimalField()
        field._set_attr_name('n')
        self.assertIsNone(field.validate(None))
        self.assertIsNone(field.validate(''))
        self.assertIsNone(field.validate('0'))
        self.assertIsNone(field.validate('1'))
        self.assertIsNone(field.validate(Decimal('1.32')))
        self.assertEqual('Must be a number', field.validate('foo'))
        self.assertEqual('Must be a number', field.validate('123h'))
        self.assertEqual('Must be a number', field.validate('0x456'))

    def test_validation_lower(self):
        field = DecimalField(lower=1)
        field._set_attr_name('n')
        self.assertIsNone(field.validate('1'))
        self.assertEqual('Must be greater than 1', field.validate('0'))

    def test_validation_upper(self):
        field = DecimalField(upper=1)
        field._set_attr_name('n')
        self.assertIsNone(field.validate('1'))
        self.assertEqual('Must be less than 1', field.validate('2'))


class StringFieldTests(unittest.TestCase):
    def test_str_with_more_than_500_chars(self):
        field = StringField()
        field._set_attr_name('n')
        self.assertEqual('Has 1501 characters and it must have 1500 or less',
                         field.validate_field('a' * (base._MAX_STRING_LENGTH + 1)))

    def test_str_with_more_than_500_chars_but_with_no_max(self):
        field = StringField(max_len=None)
        self.assertIsNone(field.validate_field('a' * 501))

    def test_str_max_len_chars(self):
        field = StringField(max_len=10)
        field._set_attr_name('n')
        self.assertEqual('Has 11 characters and it must have 10 or less', field.validate_field('a' * 11))

    def test_str_min_len_chars(self):
        field = StringField(min_len=2)
        field._set_attr_name('n')
        self.assertEqual('Has 1 characters and it must have 2 or more', field.validate_field('a'))
        self.assertIsNone(field.validate_field('aa'))
        self.assertIsNone(field.validate_field('aaa'))

    def test_str_exactly_len_chars(self):
        field = StringField(exactly_len=10)
        field._set_attr_name('n')
        self.assertEqual('Has 11 characters and it must have exactly 10', field.validate_field('a' * 11))
        self.assertEqual('Has 9 characters and it must have exactly 10', field.validate_field('a' * 9))
        self.assertIsNone(field.validate_field('a' * 10))


class DateFieldTests(unittest.TestCase):
    def test_normalization(self):
        field = DateField()
        dt = field.normalize('09/30/2000')
        datetime_date = datetime.date(2000, 9, 30)
        self.assertEqual(datetime_date, dt)
        self.assertEqual(datetime_date, field.normalize(datetime_date))

    def test_localization(self):
        field = DateField()
        dt = field.localize(datetime.date(2000, 9, 30))
        self.assertEqual('09/30/2000', dt)

    def test_validate(self):
        field = DateField()
        field._set_attr_name('d')
        self.assertIsNone(field.validate('09/30/2000'))
        self.assertIsNone(field.validate(datetime.date(2000, 9, 30)))
        self.assertEqual('Invalid date. Valid example: 12/25/2016', field.validate('09/30/a'))


class DateTimeFieldTests(unittest.TestCase):
    def test_normalization(self):
        field = DateTimeField()
        dt = field.normalize('09/30/2016, 12:00:00')
        self.assertEqual(datetime.datetime(2016, 9, 30, 15, 0, 0), dt)
        dt = field.normalize('09/30/2000 23:00:00')
        datetime_datetime = datetime.datetime(2000, 10, 1, 2, 0, 0)
        self.assertEqual(datetime_datetime, dt)
        self.assertEqual(datetime_datetime, field.normalize(datetime_datetime))

    def test_localization(self):
        field = DateTimeField()
        dt_str = field.localize(datetime.datetime(2000, 9, 30, 3, 0, 0))
        self.assertEqual('09/30/2000 00:00:00', dt_str)
        dt_str = field.localize(datetime.datetime(2000, 10, 1, 2, 0, 0))
        self.assertEqual('09/30/2000 23:00:00', dt_str)

    def test_validate(self):
        field = DateTimeField()
        field._set_attr_name('d')
        self.assertIsNone(field.validate('09/30/2000 23:59:00'))
        self.assertIsNone(field.validate(datetime.datetime(2000, 10, 1, 2, 0, 0)))
        self.assertEqual('Invalid datetime. Valid example: 12/25/2016 16:00:00',
                         field.validate('09/30/2000 23:59:a'))

    def test_date_assignment(self):
        field = DateTimeField()
        field._set_attr_name('d')
        date = datetime.datetime(2000, 9, 30)
        dt = field.normalize(date)
        self.assertEqual(date, dt)
