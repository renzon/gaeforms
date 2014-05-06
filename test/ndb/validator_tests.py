# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from decimal import Decimal
import unittest
import datetime
from google.appengine.ext import ndb
from gaevalidator.base import IntegerField
from gaevalidator.ndb.validator import ModelValidator, InvalidParams
from ndbext.property import IntegerBounded, SimpleCurrency, SimpleDecimal
from util import GAETestCase


class IntegerModelMock(ndb.Model):
    integer = ndb.IntegerProperty()
    integer_required = ndb.IntegerProperty(required=True)
    integer_repeated = ndb.IntegerProperty(repeated=True)
    integer_choices = ndb.IntegerProperty(choices=[1, 2])
    integer_default = ndb.IntegerProperty(default=0)


class IntegerModelValidator(ModelValidator):
    _model_class = IntegerModelMock


class ModelMock(ndb.Model):
    integer = IntegerBounded(required=True, lower=1, upper=2)
    currency = SimpleCurrency()
    decimal = SimpleDecimal(decimal_places=3, lower='0.001')
    str = ndb.StringProperty()
    datetime = ndb.DateTimeProperty()
    date = ndb.DateProperty()


class ModelValidator(ModelValidator):
    _model_class = ModelMock


class ModelValidatorTests(GAETestCase):
    def test_validate(self):
        validator = ModelValidator(integer=1)
        self.assertDictEqual({}, validator.validate())
        validator = ModelValidator()
        self.assertSetEqual(set(['integer']), set(validator.validate().keys()))
        validator = ModelValidator(integer=0)
        self.assertSetEqual(set(['integer']), set(validator.validate().keys()))
        validator = ModelValidator(integer=1,
                                   decimal='0.001',
                                   currency='0.01',
                                   str='a',
                                   datetime='2000/09/30 23:56:56',
                                   date='1999/08/01')
        self.assertDictEqual({}, validator.validate())
        validator = ModelValidator(integer=0,
                                   decimal='0.0001',
                                   currency='-0.01',
                                   str='a' * 501,
                                   datetime='a/09/30 23:56:56',
                                   date='1999/08/a1')
        self.assertSetEqual(set(['integer',
                                 'decimal',
                                 'currency',
                                 'str',
                                 'datetime',
                                 'date']),
                            set(validator.validate().keys()))

    def test_populate(self):
        validator = ModelValidator(integer=1,
                                   decimal='0.001',
                                   currency='0.01',
                                   str='a',
                                   datetime='2000/09/30 23:56:56',
                                   date='1999/08/01')
        property_dct = {'integer': 1,
                        'decimal': Decimal('0.001'),
                        'currency': Decimal('0.01'),
                        'str': 'a',
                        'datetime': datetime.datetime(2000, 9, 30, 23, 56, 56),
                        'date': datetime.datetime(1999, 8, 1)}
        model = validator.populate()
        self.assertIsInstance(model, ModelMock)
        self.assertDictEqual(property_dct, model.to_dict())
        model_key = model.put()



class IntegerModelValidatorTests(unittest.TestCase):
    def test_fields(self):
        properties = ['integer', 'integer_required', 'integer_repeated',
                      'integer_choices', 'integer_default']
        self.assertSetEqual(set(properties), set(IntegerModelValidator._fields.iterkeys()))
        for p in properties:
            self.assertIsInstance(IntegerModelValidator._fields[p], IntegerField)

    def test_include(self):
        properties = ['integer', 'integer_required']

        class IntegerInclude(ModelValidator):
            _model_class = IntegerModelMock
            _include = (IntegerModelMock.integer, IntegerModelMock.integer_required)

        self.assertSetEqual(set(properties), set(IntegerInclude._fields.iterkeys()))
        for p in properties:
            self.assertIsInstance(IntegerInclude._fields[p], IntegerField)

    def test_exclude(self):
        properties = ['integer_repeated', 'integer_choices', 'integer_default']

        class IntegerInclude(ModelValidator):
            _model_class = IntegerModelMock
            _exclude = (IntegerModelMock.integer, IntegerModelMock.integer_required)

        self.assertSetEqual(set(properties), set(IntegerInclude._fields.iterkeys()))
        for p in properties:
            self.assertIsInstance(IntegerInclude._fields[p], IntegerField)

    def test_include_exclude_definition_error(self):

        def f():
            class IntegerInclude(ModelValidator):
                _model_class = IntegerModelMock
                _exclude = (IntegerModelMock.integer, IntegerModelMock.integer_required)
                _include = (IntegerModelMock.integer, IntegerModelMock.integer_required)

        self.assertRaises(InvalidParams, f)

    def test_property_options(self):
        self.assertTrue(IntegerModelValidator._fields['integer_required'].required)
        self.assertTrue(IntegerModelValidator._fields['integer_repeated'].repeated)
        self.assertSetEqual(frozenset([1, 2]), IntegerModelValidator._fields['integer_choices'].choices)
        self.assertEqual(0, IntegerModelValidator._fields['integer_default'].default)

