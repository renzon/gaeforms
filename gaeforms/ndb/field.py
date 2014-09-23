# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

class BooleanField(BaseField):
    def validate_field(self, value):
        try:
            value = self.normalize_field(value)
            return super(BooleanField, self).validate_field(value)
        except:
            return _('Must be true or false')

    def normalize_field(self, value):
        if value == '':
            value = None
        elif value is not None:
            value=value.upper()
            if value=='TRUE':
                return True
            elif value=='FALSE':
                return False
            raise Exception(msg='Should be True or False')

        return super(BooleanField, self).normalize_field(value)

    def localize(self, value):
        return value
