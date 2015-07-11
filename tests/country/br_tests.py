# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import unittest

from google.appengine.ext.ndb import Model
import webapp2


# workaround to enable i18n tests
from gaeforms.country.br.field import CepField, CpfField, CnpjField
from gaeforms.country.br.property import CepProperty, CpfProperty, CnpjProperty
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


class CpfFieldTests(unittest.TestCase):
    def test_normalization(self):
        field = CpfField()
        self.assertIsNone(field.normalize(''))
        self.assertIsNone(field.normalize(None))
        self.assertEquals('06768725815', field.normalize('067.687.258-15'))
        self.assertEquals('13731760592', field.normalize('13731760592'))

    def test_localization(self):
        field = CpfField()
        self.assertEqual('', field.localize(''))
        self.assertEqual('', field.localize(None))
        self.assertEquals('067.687.258-15', field.localize('06768725815'))

    def test_validate(self):
        field = CpfField()
        self.assertIsNone(field.validate('06768725815'))
        self.assertIsNone(field.validate('067.687.258-15'))
        self.assertIsNone(field.validate('067-687-258.15'))
        self.assertEqual('CPF must have exactly 11 characters', field.validate('0676872581'))
        self.assertEqual('CPF must have exactly 11 characters', field.validate('067687258155'))
        self.assertEqual('Invalid CPF', field.validate('067.687.258-00'))


class CpfPropertyTests(GAETestCase):
    def test_property_to_field_link(self):
        class StubModel(Model):
            cpf = CpfProperty(required=True)

        class StubForm(ModelForm):
            _model_class = StubModel

        form = StubForm(cpf='')
        self.assertDictEqual({'cpf': u'Required field'}, form.validate())

        form.cpf = '912.890.377-36'
        self.assertDictEqual({}, form.validate())

        model = form.fill_model()
        self.assertEqual('91289037736', model.cpf)

        self.assertRaises(BoundaryError, StubModel, cpf='9128903773')
        self.assertRaises(BoundaryError, StubModel, cpf='912890377361')


class CnpjFieldTests(unittest.TestCase):

    def test_validate(self):
        cnpj_field = CnpjField()
        self.assertIsNone(cnpj_field.validate('69435154000102'))
        self.assertIsNone(cnpj_field.validate('69.435.154/0001-02'))
        self.assertIsNone(cnpj_field.validate('53.612.734/0001-98'))
        self.assertEquals('CNPJ must contain only numbers', cnpj_field.validate('1231231aa12342'))
        self.assertEquals('Invalid CNPJ', cnpj_field.validate('12312313212342'))
        self.assertEquals('CNPJ must have exactly 14 characters', cnpj_field.validate('6188261300019'))

    def test_normalization(self):
        field = CnpjField()
        self.assertIsNone(field.normalize(''))
        self.assertIsNone(field.normalize(None))
        self.assertEquals('69435154000102', field.normalize('69.435.154/0001-02'))
        self.assertEquals('69435154000102', field.normalize('69435154000102'))

    def test_localization(self):
        field = CnpjField()
        self.assertEqual('', field.localize(''))
        self.assertEqual('', field.localize(None))
        self.assertEquals('69.435.154/0001-02', field.localize('69435154000102'))


class CnpjPropertyTests(GAETestCase):
    def test_property_to_field_link(self):
        class StubModel(Model):
            cnpj = CnpjProperty(required=True)

        class StubForm(ModelForm):
            _model_class = StubModel

        form = StubForm(cnpj='')
        self.assertDictEqual({'cnpj': u'Required field'}, form.validate())

        form.cnpj = '69.435.154/0001-02'
        self.assertDictEqual({}, form.validate())

        model = form.fill_model()
        self.assertEqual('69435154000102', model.cnpj)

        self.assertRaises(BoundaryError, StubModel, cnpj='694351540001')
        self.assertRaises(BoundaryError, StubModel, cnpj='6943515400010212')

















