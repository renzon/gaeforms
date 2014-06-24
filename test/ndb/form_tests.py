# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from decimal import Decimal
import unittest
import datetime
from google.appengine.ext import ndb
import webapp2
from gaeforms.base import IntegerField
from gaeforms.ndb.form import ModelForm, InvalidParams
from ndbext.property import IntegerBounded, SimpleCurrency, SimpleDecimal
from util import GAETestCase
from webapp2_extras import i18n
from gaeforms.base import BaseField, Form, IntegerField, DecimalField, StringField, DateField, DateTimeField

app = webapp2.WSGIApplication(
    [webapp2.Route('/', None, name='upload_handler')])

request = webapp2.Request({'SERVER_NAME': 'test', 'SERVER_PORT': 80,
                           'wsgi.url_scheme': 'http'})
request.app = app
app.set_globals(app=app, request=request)

i18n.default_config['default_timezone'] = 'America/Sao_Paulo'


class IntegerModelMock(ndb.Model):
    integer = ndb.IntegerProperty()
    integer_required = ndb.IntegerProperty(required=True)
    integer_repeated = ndb.IntegerProperty(repeated=True)
    integer_choices = ndb.IntegerProperty(choices=[1, 2])
    integer_default = ndb.IntegerProperty(default=0)


class IntegerModelForm(ModelForm):
    _model_class = IntegerModelMock


class ModelMock(ndb.Model):
    integer = IntegerBounded(required=True, lower=1, upper=2)
    i = ndb.IntegerProperty(default=1)
    currency = SimpleCurrency()
    decimal = SimpleDecimal(decimal_places=3, lower='0.001')
    str = ndb.StringProperty()
    datetime = ndb.DateTimeProperty()
    date = ndb.DateProperty()


class ModelFormMock(ModelForm):
    _model_class = ModelMock


class ModelFormOverriding(ModelForm):
    _model_class = ModelMock
    integer = IntegerField(required=True)


class ModelFormTests(GAETestCase):
    def test_overriding(self):
        validator = ModelFormOverriding(integer='0')
        self.assertDictEqual({}, validator.validate(),
                               'integer with no bounds should be used once it is overriden on ModelValidatorOverriging')

    def test_validate(self):
        validator = ModelFormMock(integer='1')
        self.assertDictEqual({}, validator.validate())
        validator = ModelFormMock()
        self.assertSetEqual(set(['integer']), set(validator.validate().keys()))
        validator = ModelFormMock(integer='0')
        self.assertSetEqual(set(['integer']), set(validator.validate().keys()))
        validator = ModelFormMock(integer='1',
                                  decimal='0.001',
                                  currency='0.01',
                                  str='a',
                                  datetime='30/09/2000 23:56:56',
                                  date='08/01/1999')
        self.assertDictEqual({}, validator.validate())
        validator = ModelFormMock(integer='0',
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

    def test_populate_model(self):
        model_form = ModelFormMock(integer='1',
                                   decimal='0.001',
                                   currency='0.01',
                                   str='a',
                                   datetime='09/30/2000 23:56:56',
                                   date='08/01/1999')
        property_dct = {'integer': 1,
                        'i': 1,
                        'decimal': Decimal('0.001'),
                        'currency': Decimal('0.01'),
                        'str': 'a',
                        'datetime': datetime.datetime(2000, 10, 1, 2, 56, 56),
                        'date': datetime.date(1999, 8, 1)}
        model = model_form.populate_model()
        self.assertIsInstance(model, ModelMock)
        self.assertDictEqual(property_dct, model.to_dict())
        model_key = model.put()
        model_form = ModelFormMock(integer='2',
                                   decimal='3.001',
                                   currency='4.01',
                                   str='b',
                                   datetime='09/30/2000 23:56:56',
                                   date='08/01/1999')
        property_dct = {'integer': 2,
                        'i': 1,
                        'decimal': Decimal('3.001'),
                        'currency': Decimal('4.01'),
                        'str': 'b',
                        'datetime': datetime.datetime(2000, 10, 1, 2, 56, 56),
                        'date': datetime.date(1999, 8, 1)}
        model_form.populate_model(model)
        self.assertIsInstance(model, ModelMock)
        self.assertDictEqual(property_dct, model.to_dict())
        self.assertEqual(model_key, model.key)

    def test_populate_form(self):
        model_form = ModelFormMock()
        model = ModelMock(integer=1,
                          decimal=Decimal('0.001'),
                          currency=Decimal('0.01'),
                          str='a',
                          datetime=datetime.datetime(2000, 9, 30, 23, 56, 56),
                          date=datetime.datetime(1999, 8, 1))
        localized_dct = model_form.populate_form(model)
        self.assertDictEqual({'integer': '1',
                              'i': '1',
                              'decimal': '0.001',
                              'currency': '0.01',
                              'str': 'a',
                              'datetime': '09/30/2000 20:56:56',
                              'date': '08/01/1999'}, localized_dct)


class IntegerModelFormTests(unittest.TestCase):
    def test_fields(self):
        properties = ['integer', 'integer_required', 'integer_repeated',
                      'integer_choices', 'integer_default']
        self.assertSetEqual(set(properties), set(IntegerModelForm._fields.iterkeys()))
        for p in properties:
            self.assertIsInstance(IntegerModelForm._fields[p], IntegerField)

    def test_include(self):
        properties = ['integer', 'integer_required']

        class IntegerInclude(ModelForm):
            _model_class = IntegerModelMock
            _include = (IntegerModelMock.integer, IntegerModelMock.integer_required)

        self.assertSetEqual(set(properties), set(IntegerInclude._fields.iterkeys()))
        for p in properties:
            self.assertIsInstance(IntegerInclude._fields[p], IntegerField)

    def test_exclude(self):
        properties = ['integer_repeated', 'integer_choices', 'integer_default']

        class IntegerInclude(ModelForm):
            _model_class = IntegerModelMock
            _exclude = (IntegerModelMock.integer, IntegerModelMock.integer_required)

        self.assertSetEqual(set(properties), set(IntegerInclude._fields.iterkeys()))
        for p in properties:
            self.assertIsInstance(IntegerInclude._fields[p], IntegerField)

    def test_include_exclude_definition_error(self):

        def f():
            class IntegerInclude(ModelForm):
                _model_class = IntegerModelMock
                _exclude = (IntegerModelMock.integer, IntegerModelMock.integer_required)
                _include = (IntegerModelMock.integer, IntegerModelMock.integer_required)

        self.assertRaises(InvalidParams, f)

    def test_property_options(self):
        self.assertTrue(IntegerModelForm._fields['integer_required'].required)
        self.assertTrue(IntegerModelForm._fields['integer_repeated'].repeated)
        self.assertSetEqual(frozenset([1, 2]), IntegerModelForm._fields['integer_choices'].choices)
        self.assertEqual(0, IntegerModelForm._fields['integer_default'].default)

