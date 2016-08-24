# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from itertools import izip
import operator

from gettext import gettext as _

from gaeforms.base import BaseField


def mod11(value):
    numbers = [int(x) for x in value]
    range_max = len(numbers) + 1
    result = sum(map(operator.mul, numbers, range(range_max, 1, -1)))
    result = 11 - (result % 11)
    if result >= 10:
        result = 0
    return result


class CepField(BaseField):
    def validate_field(self, value):
        if value:
            value = self.normalize_field(value)
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

    def localize_field(self, value):
        if value:
            return '%s-%s' % (value[:5], value[5:])
        return super(CepField, self).localize_field(value)


class CpfField(BaseField):
    def validate_field(self, value):
        if value:
            value = self.normalize_field(value)
            if len(value) != 11:
                return _('CPF must have exactly 11 characters')
            try:
                int(value)
            except:
                return _('CPF must contain only numbers')
            user_dv = value[-2:]
            real_dv = self._calculate_dv(value[:9])
            if user_dv != real_dv:
                return _('Invalid CPF')

        return super(CpfField, self).validate_field(value)

    def normalize_field(self, value):
        if value:
            return value.replace('-', '').replace('.', '')
        elif value == '':
            value = None
        return super(CpfField, self).normalize_field(value)

    def localize_field(self, value):
        if value:
            return '%s.%s.%s-%s' % (value[:3], value[3:6], value[6:9], value[9:11])
        return super(CpfField, self).localize_field(value)

    def _calculate_dv(self, value):
        dv1 = mod11(value)
        dv2 = mod11('%s%s' % (value, dv1))
        return str(dv1) + str(dv2)


class CnpjField(BaseField):
    def validate_field(self, number):
        if not number:
            return super(CnpjField, self).validate_field(number)

        number = self.normalize_field(number)

        if len(number) != 14:
            return _('CNPJ must have exactly 14 characters')

        try:
            int(number)
        except:
            return _('CNPJ must contain only numbers')

        first_weights = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        second_weights = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        first_part = number[:12]

        first_digit = number[12]
        second_digit = number[13]

        if (first_digit == self.__check_digit(first_part, first_weights) and
                    second_digit == self.__check_digit(number[:13], second_weights)):
            return None
        else:
            return _('Invalid CNPJ')

    def normalize_field(self, value):
        if value:
            return value.replace('-', '').replace('.', '').replace('/', '')
        elif value == '':
            value = None
        return super(CnpjField, self).normalize_field(value)

    def localize_field(self, value):
        if value:
            return '%s.%s.%s/%s-%s' % (value[:2], value[2:5], value[5:8], value[8:12], value[12:14])
        return super(CnpjField, self).localize_field(value)

    @staticmethod
    def __check_digit(number, weights):
        total = sum((int(n) * w for n, w in izip(number, weights)))

        rest_division = total % 11
        if rest_division < 2:
            return '0'
        return str(11 - rest_division)
