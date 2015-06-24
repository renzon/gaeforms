# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from webapp2_extras.i18n import gettext as _
from gaeforms.base import BaseField


class CepField(BaseField):
    def validate_field(self, value):
        if value:
            value = value.replace('-', '')
            if len(value) != 8:
                return _('CEP must have exactly 8 characters')
            try:
                int(value)
            except:
                return _('CEP must contain only numbers')
        return super(CepField, self).validate_field(value)

    def normalize_field(self, value):
        if value:
            return value.replace('-', '')
        elif value == '':
            value = None
        return super(CepField, self).normalize_field(value)


    def localize(self, value):
        if value:
            return '%s-%s' % (value[:5], value[5:])
        return super(CepField, self).localize(value)