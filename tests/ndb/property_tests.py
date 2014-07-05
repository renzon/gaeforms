# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from decimal import Decimal, InvalidOperation
import unittest

from google.appengine.ext import ndb

from gaeforms.ndb.property import IntegerBounded, BoundaryError, SimpleDecimal, SimpleCurrency, FloatBounded
from util import GAETestCase


class IntegerModelMock(ndb.Model):
    lower = IntegerBounded(lower=0)
    upper = IntegerBounded(upper=3)
    lower_and_upper = IntegerBounded(lower=-1, upper=1)


class IntegerBoundedTests(unittest.TestCase):
    def test_lower(self):
        self.assertRaises(BoundaryError, IntegerModelMock, lower=-1)

        # no exceptions with bigger values
        IntegerModelMock(lower=0)
        IntegerModelMock(lower=99999999999999999999)

    def test_lower_and_upper(self):
        self.assertRaises(BoundaryError, IntegerModelMock, lower_and_upper=-3)
        self.assertRaises(BoundaryError, IntegerModelMock, lower_and_upper=2)

        # no exceptions with values in interval
        IntegerModelMock(lower_and_upper=0)

    def test_upper(self):
        self.assertRaises(BoundaryError, IntegerModelMock, upper=4)

        # no exceptions with bigger values
        IntegerModelMock(upper=3)
        IntegerModelMock(upper=-99999999999999999999)

    def test_none(self):
        # asserting nothing hapens with None values
        IntegerModelMock(lower=None, upper=None, lower_and_upper=None)


class FloatModelMock(ndb.Model):
    lower = FloatBounded(lower=0.1)
    upper = FloatBounded(upper=3.1)
    lower_and_upper = FloatBounded(lower=-1.1, upper=1.2)


class FloatBoundedTests(unittest.TestCase):
    def test_lower(self):
        self.assertRaises(BoundaryError, FloatModelMock, lower=-1)

        # no exceptions with bigger values
        FloatModelMock(lower=0.1)
        FloatModelMock(lower=1.1)
        FloatModelMock(lower=99999999999999999999)

    def test_lower_and_upper(self):
        self.assertRaises(BoundaryError, FloatModelMock, lower_and_upper=-3)
        self.assertRaises(BoundaryError, FloatModelMock, lower_and_upper=2)

        # no exceptions with values in interval
        FloatModelMock(lower_and_upper=0)

    def test_upper(self):
        self.assertRaises(BoundaryError, FloatModelMock, upper=4)

        # no exceptions with bigger values
        FloatModelMock(upper=3)
        FloatModelMock(upper=1.2)
        FloatModelMock(upper=-99999999999999999999)

    def test_none(self):
        # asserting nothing hapens with None values
        FloatModelMock(lower=None, upper=None, lower_and_upper=None)


class SimpleDecimalModelMock(ndb.Model):
    value = SimpleDecimal(lower=-1.22, upper=1.22)


class SimpleDecimalTests(GAETestCase):
    def test_data_transformation(self):
        model = SimpleDecimalModelMock(value='1.221')
        self.assertEqual(Decimal('1.22'), model.value)

    def test_lower_and_upper(self):
        self.assertRaises(BoundaryError, SimpleDecimalModelMock, value=-1.23)
        self.assertRaises(BoundaryError, SimpleDecimalModelMock, value=1.23)
        model = SimpleDecimalModelMock(value=-1.22)
        model.put()
        model.value = 1.22
        model.put()

    def test_inputs(self):
        self.assertRaises(InvalidOperation, SimpleDecimalModelMock, value='a')
        model = SimpleDecimalModelMock(value='1')
        model.put()
        self.assertEquals(Decimal('1.00'), model.value)

        model = SimpleDecimalModelMock(value=1)
        model.put()
        self.assertEquals(Decimal('1.00'), model.value)

        model = SimpleDecimalModelMock(value='1.1111')
        model.put()
        self.assertEquals(Decimal('1.11'), model.value)

        model = SimpleDecimalModelMock(value=1.1111)
        model.put()
        self.assertEquals(Decimal('1.11'), model.value)

        model = SimpleDecimalModelMock(value='1.117')
        model.put()
        self.assertEquals(Decimal('1.12'), model.value)

        model = SimpleDecimalModelMock(value=1.117)
        model.put()
        self.assertEquals(Decimal('1.12'), model.value)

    def test_decimal_places(self):
        class ModelMock(ndb.Model):
            value = SimpleDecimal(decimal_places=3)

        model = ModelMock(value=1)
        model.put()
        self.assertEquals(Decimal('1.000'), model.value)

        class ModelMock(ndb.Model):
            value = SimpleDecimal(decimal_places=1)

        model = ModelMock(value=1)
        model.put()
        self.assertEquals(Decimal('1.0'), model.value)

    def test_query(self):
        class ModelMock(ndb.Model):
            value = SimpleDecimal()

        models = [ModelMock(value='0.0%s' % i) for i in xrange(10)]
        ndb.put_multi(models)
        result = ModelMock.query(ModelMock.value < Decimal('0.03')).order(ModelMock.value).fetch()
        self.assertListEqual([Decimal('0.00'), Decimal('0.01'), Decimal('0.02')], [m.value for m in result])
        result = ModelMock.query(ModelMock.value >= Decimal('0.07')).order(ModelMock.value).fetch()
        self.assertListEqual([Decimal('0.07'), Decimal('0.08'), Decimal('0.09')], [m.value for m in result])


class SimpleCurrencyTests(GAETestCase):
    def test_default_lower(self):
        '''
        Once SimpleCurrency inherits from SimpleDecimal, it's only necessary testing
        default lower 0 value
        '''

        class ModelMock(ndb.Model):
            currency = SimpleCurrency()

        self.assertRaises(BoundaryError, ModelMock, currency='-0.01')
        ModelMock(currency='0').put()
