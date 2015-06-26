# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from google.appengine.ext.ndb.model import StringProperty
from gaeforms.country.br.field import CepField
from gaeforms.ndb.form import registry


class CepProperty(StringProperty):
    """
    Class created only to link with CepField
    """
    pass


registry(CepProperty, CepField)
