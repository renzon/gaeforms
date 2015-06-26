# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import unittest

from google.appengine.ext.ndb import Model
import webapp2


# workaroung to enable i18n tests
from gaeforms.country.br.field import CepField
from gaeforms.country.br.property import CepProperty
from gaeforms.ndb.form import ModelForm
from gaeforms.ndb.property import BoundaryError
from util import GAETestCase

app = webapp2.WSGIApplication(
    [webapp2.Route('/', None, name='upload_handler')])

request = webapp2.Request({'SERVER_NAME': 'test', 'SERVER_PORT': 80,
                           'wsgi.url_scheme': 'http'})
request.app = app
app.set_globals(app=app, request=request)
# end fo workaround


def error_msg(attr_name):
    return '%s has error' % attr_name


class CepFieldTests(unittest.TestCase):
    def test_normalization(self):
        field = CepField()
        self.assertIsNone(field.normalize(''))
        self.assertIsNone(field.normalize(None))
        self.assertEqual('12345678', field.normalize('12345-678'))
        self.assertEqual('12345678', field.normalize('12345678'))

    def test_localization(self):
        field = CepField()
        self.assertEqual('', field.localize(''))
        self.assertEqual('', field.localize(None))
        self.assertEqual('12345-678', field.localize('12345678'))

    def test_validate(self):
        field = CepField()
        field._set_attr_name('d')
        self.assertIsNone(field.validate('12345678'))
        self.assertIsNone(field.validate('12345-678'))
        self.assertIsNone(field.validate('1234567-8'))
        self.assertEqual('CEP must have exactly 8 characters', field.validate('1234567'))
        self.assertEqual('CEP must have exactly 8 characters', field.validate('123456789'))
        self.assertEqual('CEP must contain only numbers', field.validate('1234567a'))


class CepPropertyTests(GAETestCase):
    def test_property_to_field_link(self):
        class StubModel(Model):
            cep = CepProperty(required=True)

        class StubForm(ModelForm):
            _model_class = StubModel

        form = StubForm(cep='')
        self.assertDictEqual({'cep': u'Required field'}, form.validate())

        form.cep = '12345-678'
        self.assertDictEqual({}, form.validate())

        model = form.fill_model()
        self.assertEqual('12345678', model.cep)

        self.assertRaises(BoundaryError, StubModel, cep='1234567')
        self.assertRaises(BoundaryError, StubModel, cep='123456789')
