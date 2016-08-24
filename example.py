# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import os
import sys

from google.appengine.ext.ndb.model import Model, IntegerProperty, StringProperty, BooleanProperty

from gaeforms.country.br.property import CepProperty
from gaeforms.ndb.form import ModelForm

if 'GAE_SDK' in os.environ:
    SDK_PATH = os.environ['GAE_SDK']

    sys.path.insert(0, SDK_PATH)

    import dev_appserver

    dev_appserver.fix_sys_path()


class User(Model):
    name = StringProperty(required=True)
    age = IntegerProperty()


class UserForm(ModelForm):
    _model_class = User


class Address(Model):
    cep_declared = BooleanProperty(default=False)
    cep = CepProperty()


class AddressForm(ModelForm):
    _model_class = Address

    def validate(self):
        errors = super(AddressForm, self).validate()
        normalized_dct = self.normalize()
        if normalized_dct['cep_declared'] is True and not self.cep:
            errors['cep'] = 'If CEP is declared it should not be empty'
        return errors
