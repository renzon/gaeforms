# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from google.appengine.ext.ndb.model import StringProperty
from gaeforms.country.br.field import CepField
from gaeforms.ndb.form import registry
from gaeforms.ndb.property import BoundaryError


class CepProperty(StringProperty):
    """
    Class created related with Brazilian postal code (CEP)
    """

    def _validate(self, value):
        if len(value) != 8:
            raise BoundaryError('%s should have exactly 8 characters' % value)


registry(CepProperty, CepField)
