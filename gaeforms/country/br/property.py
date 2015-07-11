# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from google.appengine.ext.ndb.model import StringProperty
from gaeforms.ndb.property import BoundaryError
from gaeforms.country.br.field import CepField, CpfField, CnpjField
from gaeforms.ndb.form import registry


class CepProperty(StringProperty):
    """
    Class related with Brazilian postal code (CEP)
    """

    def _validate(self, value):
        if len(value) != 8:
            raise BoundaryError('%s should have exactly 8 characters' % value)


registry(CepProperty, CepField)


class CpfProperty(StringProperty):
    """
    Class related with Brazilian personal document identifier (CPF)
    """

    def _validate(self, value):
        if len(value) != 11:
            raise BoundaryError('%s should have exactly 11 characters' % value)


registry(CpfProperty, CpfField)


class CnpjProperty(StringProperty):
    """
    """

    def _validate(self, value):
        if len(value) != 14:
            raise BoundaryError('%s should have exactly 14 characters' % value)


registry(CnpjProperty, CnpjField)
