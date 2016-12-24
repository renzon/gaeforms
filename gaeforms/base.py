# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import datetime
import re
from decimal import Decimal
from gettext import gettext as _

from babel import dates
from babel.dates import parse_date, format_date, format_datetime
from babel.numbers import parse_decimal, format_number, format_decimal
from google.appengine.ext import ndb
from google.appengine.ext.ndb import Model

from gaeforms import settings


class BaseField(object):
    def __init__(self, required=False, default=None, repeated=False, choices=None):
        self.repeated = repeated
        self.choices = choices
        self.default = default
        self.required = required
        self._attr = ''

    def set_options(self, model_property):
        self.required = model_property._required
        self.default = model_property._default
        self.repeated = model_property._repeated
        self.choices = model_property._choices

    def _set_attr_name(self, name):
        self._attr = name

    def __set__(self, instance, value):
        setattr(instance, '_' + self._attr, value)

    def validate_field(self, value):
        '''
        Method that must validate the value
        It must return None if the value is valid and a error msg otherelse.
        Ex: If expected input must be int, validate should a return a msg like
        "The filed must be a integer value"
        '''
        if self.choices:
            value = self.normalize_field(value)
            if value in self.choices:
                return None
            return _('Must be one of: %(choices)s') % {'choices': '; '.join(self.choices)}
        if self.default is not None:
            if value is None or value == '':
                value = self.default
        if self.required and (value is None or value == ''):
            return _('Required field')

    def __get__(self, instance, owner):
        return getattr(instance, '_' + self._attr)

    def validate(self, value):
        if self.repeated:
            if value:
                error = None
                for v in value:
                    error = self.validate_field(v)
                return error
            else:
                value = None
        return self.validate_field(value)

    def _execute_one_or_repeated(self, fcn, value):
        if self.repeated:
            if value:
                return [fcn(v) for v in value]
            return []
        return fcn(value)

    def normalize(self, value):
        """
        Normalizes a value to be stored on db. Transforms string from web requests on db object, removing any
        localization
        :param value: value to be normalize
        :return: a normalized value
        """
        return self._execute_one_or_repeated(self.normalize_field, value)

    def normalize_field(self, value):
        """
        Method that must transform the value from string
        Ex: if the expected type is int, it should return int(self._attr)

        """
        if self.default is not None:
            if value is None or value == '':
                value = self.default
        return value

    def localize(self, value):
        """
        Localizes a value to be sent to clients. Transforms object on localized strings. Must make the opposite of
        normalizes
        :param value: value to be localized
        :return: a localized value
        """
        return self._execute_one_or_repeated(self.localize_field, value)

    def localize_field(self, value):
        """
        Method that must transform the value from object to localized string

        """
        if self.default is not None:
            if value is None or value == '':
                value = self.default
        return value or ''


_MAX_STRING_LENGTH = 1500


# Concrete fields
class StringField(BaseField):
    def __init__(self, required=False, default=None, repeated=False, choices=None, max_len=_MAX_STRING_LENGTH,
                 exactly_len=None, min_len=None):
        super(StringField, self).__init__(required, default, repeated, choices)
        self.min_len = min_len
        self.exactly_len = exactly_len
        self.max_len = max_len

    def set_options(self, model_property):
        super(StringField, self).set_options(model_property)
        self.max_len = getattr(model_property, 'max_len', None)
        if self.max_len is None:
            self.max_len = _MAX_STRING_LENGTH if model_property._indexed else None
        self.exactly_len = getattr(model_property, 'exactly_len', None)
        self.min_len = getattr(model_property, 'min_len', None)

    def validate_field(self, value):
        if value is not None:
            len_value = len(value)
            if self.exactly_len is not None and len_value != self.exactly_len:
                return _('Has %(len)s characters and it must have exactly %(exactly_len)s') % {'len': len_value,
                                                                                               'exactly_len': self.exactly_len}
            if self.max_len and len_value > self.max_len:
                return _('Has %(len)s characters and it must have %(max_len)s or less') % {'len': len_value,
                                                                                           'max_len': self.max_len}
            if self.min_len and len_value < self.min_len:
                return _('Has %(len)s characters and it must have %(min_len)s or more') % {'len': len_value,
                                                                                           'min_len': self.min_len}

        return super(StringField, self).validate_field(value)


class EmailField(StringField):
    def validate_field(self, value):
        if value and not re.match(r'[^@]+@[^@]+\.[^@]+', value):
            return _('Invalid email')

        return super(EmailField, self).validate_field(value)


class KeyField(BaseField):
    def __init__(self, kind=None, required=False, default=None, repeated=False, choices=None):
        super(KeyField, self).__init__(required, default, repeated, choices)
        self.kind = kind

    def set_options(self, model_property):
        super(KeyField, self).set_options(model_property)
        self.kind = model_property._kind

    def validate_field(self, value):
        if value == '':
            value = None
        elif value is not None:
            if isinstance(value, basestring):
                try:
                    id = int(value)
                    if self.kind:
                        value = ndb.Key(self.kind, id)
                    else:
                        return _("Key's kind should be defined")
                except ValueError:
                    try:
                        value = ndb.Key(urlsafe=value)
                    except:
                        return _('Invalid key')
            elif isinstance(value, Model) and value.key:
                return
        return super(KeyField, self).validate_field(value)

    def normalize_field(self, value):
        if value == '':
            value = None
        elif value is not None:
            if isinstance(value, basestring):
                try:
                    id = int(value)
                    if self.kind:
                        value = ndb.Key(self.kind, id)
                    else:
                        raise Exception("Key's kind should be defined")
                except ValueError:
                    try:
                        value = ndb.Key(urlsafe=value)
                    except:
                        raise Exception('Invalid key')
            elif isinstance(value, Model):
                return value.key
        return super(KeyField, self).normalize_field(value)

    def localize_field(self, value):
        if value:
            return value.id()
        return super(KeyField, self).localize_field(value)


class IntegerField(BaseField):
    def __init__(self, required=False, default=None, repeated=False, choices=None, lower=None, upper=None):
        super(IntegerField, self).__init__(required, default, repeated, choices)
        self.upper = upper
        self.lower = lower

    def set_options(self, model_property):
        super(IntegerField, self).set_options(model_property)
        self.lower = getattr(model_property, 'lower', None)
        self.upper = getattr(model_property, 'upper', None)

    def validate_field(self, value):
        try:
            value = self.normalize_field(value)
            if value is not None:
                if self.lower is not None and self.lower > value:
                    return _('Must be greater than %(lower)s') % {'lower': self.lower}
                if self.upper is not None and self.upper < value:
                    return _('Must be less than %(upper)s') % {'upper': self.upper}
            return super(IntegerField, self).validate_field(value)
        except:
            return _('Must be integer')

    def normalize_field(self, value):
        if value == '':
            value = None
        if isinstance(value, int):
            return value
        elif value is not None:
            locale = settings.get_locale()
            value = int(parse_decimal(value, locale=locale))
        return super(IntegerField, self).normalize_field(value)

    def localize_field(self, value):
        if value is not None:
            return int(value)
        return super(IntegerField, self).localize_field(value)


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
        if isinstance(value, bool):
            return value
        elif value is not None:
            value = value.upper()
            if value == 'TRUE':
                return True
            elif value == 'FALSE':
                return False
            raise Exception(msg='Should be True or False')

        return super(BooleanField, self).normalize_field(value)

    def localize(self, value):
        return value


class FloatField(BaseField):
    def __init__(self, required=False, default=None, repeated=False, choices=None, lower=None, upper=None):
        super(FloatField, self).__init__(required, default, repeated, choices)
        self.upper = upper
        self.lower = lower

    def validate_field(self, value):
        try:
            value = self.normalize_field(value)
            if value is not None:
                if self.lower is not None and self.lower > value:
                    return _('Must be greater than %(lower)s') % {'lower': self.lower}
                if self.upper is not None and self.upper < value:
                    return _('Must be less than %(upper)s') % {'upper': self.upper}
            return super(FloatField, self).validate_field(value)
        except:
            return _('Must be a number')

    def normalize_field(self, value):
        if isinstance(value, (int, float)):
            return value
        if value == '':
            value = None
        elif value is not None:
            value = float(parse_decimal(value, locale=settings.get_locale()))
        return super(FloatField, self).normalize_field(value)

    def localize_field(self, value):
        if value is not None and value != '':
            return format_decimal(value, locale=settings.get_locale())
        return super(FloatField, self).localize_field(value)


class DecimalField(BaseField):
    def _to_decimal(self, number):
        return None if number is None else self.normalize_field(unicode(number))

    def __init__(self, required=False, default=None, repeated=False, choices=None, decimal_places=2, lower=None,
                 upper=None):
        super(DecimalField, self).__init__(required, default, repeated, choices)
        self.decimal_places = decimal_places
        self.__multiplier = (10 ** self.decimal_places)
        self.upper = self._to_decimal(upper)
        self.lower = self._to_decimal(lower)

    def set_options(self, model_property):
        super(DecimalField, self).set_options(model_property)
        self.__multiplier = (10 ** model_property.decimal_places)
        self.decimal_places = model_property.decimal_places
        self.lower = self._to_decimal(getattr(model_property, 'lower', None))
        self.upper = self._to_decimal(getattr(model_property, 'upper', None))

    def validate_field(self, value):
        try:
            value = self.normalize_field(value)
            if value is not None:
                if self.lower is not None and self.lower > value:
                    return _('Must be greater than %(lower)s') % {'lower': self.lower}
                if self.upper is not None and self.upper < value:
                    return _('Must be less than %(upper)s') % {'upper': self.upper}
            return super(DecimalField, self).validate_field(value)
        except:
            return _('Must be a number')

    def normalize_field(self, value):
        if isinstance(value, Decimal):
            return value
        if value == '':
            value = None
        elif value is not None:
            value = parse_decimal(value, locale=settings.get_locale())
            rounded = int(round(Decimal(value) * self.__multiplier))
            value = Decimal(rounded) / self.__multiplier
        return super(DecimalField, self).normalize_field(value)

    def localize_field(self, value):
        if value is not None and value != '':
            return format_decimal(value, locale=settings.get_locale())
        return super(DecimalField, self).localize_field(value)


class DateFieldMixin(object):
    def localize_date(self, value):
        if isinstance(value, datetime.datetime):
            value = datetime.date(value.year, value.month, value.day)
        pattern = self.get_date_format()
        return format_date(value, format=pattern)

    def get_date_format(self):
        pattern = dates.get_date_format(format=self.format, locale=settings.get_locale()).pattern
        for c in ('M', 'd', 'yy'):
            double_char = c * 2
            if double_char not in pattern:
                pattern = pattern.replace(c, double_char)
        return pattern

    def get_time_format(self):
        return 'HH:mm:ss'


class DateField(BaseField, DateFieldMixin):
    def __init__(self, required=False, default=None, repeated=False, choices=None, format='short'):
        super(DateField, self).__init__(required, default, repeated, choices)
        self.format = format

    def normalize_field(self, value):
        if isinstance(value, basestring):
            return parse_date(value, locale=settings.get_locale())
        return super(DateField, self).normalize_field(value)

    def validate_field(self, value):
        try:
            value = self.normalize_field(value)
            return super(DateField, self).validate_field(value)
        except Exception:
            example = self.localize_field(datetime.date(2016, 12, 25))
            return _('Invalid date. Valid example: %(date)s') % {'date': example}

    def localize_field(self, value):
        if value:
            return self.localize_date(value)

        return super(DateField, self).localize_field(value)


class DateTimeField(BaseField, DateFieldMixin):
    def __init__(self, required=False, default=None, repeated=False, choices=None, format='short'):
        super(DateTimeField, self).__init__(required, default, repeated, choices)
        self.format = format

    def normalize_field(self, value):
        if isinstance(value, basestring):
            locale = settings.get_locale()

            date_str, time_str = value.split(' ')
            date = dates.parse_date(date_str, locale)
            time = dates.parse_time(time_str, locale)
            dtime = datetime.datetime(date.year, date.month, date.day, time.hour, time.minute, time.second)
            dtime = settings.get_timezone().localize(dtime)
            utc_dt = dates.UTC.normalize(dtime)
            return utc_dt.replace(tzinfo=None)

        return super(DateTimeField, self).normalize_field(value)

    def validate_field(self, value):
        try:
            value = self.normalize_field(value)
            return super(DateTimeField, self).validate_field(value)
        except:
            example = self.localize(datetime.datetime(2016, 12, 25, 18, 0, 0))
            return _('Invalid datetime. Valid example: %(datetime)s') % {'datetime': example}

    def localize_field(self, value):
        if value:
            utc_dt = value.replace(tzinfo=dates.UTC)
            local_dt = settings.get_timezone().normalize(utc_dt)

            pattern = '{0} {1}'.format(self.get_date_format(), self.get_time_format())
            return format_datetime(local_dt, pattern)
        return super(DateTimeField, self).localize_field(value)


class _FormMetaclass(type):
    def __new__(cls, class_to_be_created_name, bases, attrs):
        def set_descriptor_attr_name(descriptor, name):
            descriptor._set_attr_name(name)
            return descriptor

        descriptors = (set_descriptor_attr_name(attr_value, attr_name)
                       for attr_name, attr_value in attrs.iteritems()
                       if hasattr(attr_value, '_set_attr_name'))

        attrs['_fields'] = {d._attr: d for d in descriptors}

        return super(_FormMetaclass, cls).__new__(cls, class_to_be_created_name, bases, attrs)


class Form(object):
    _fields = ()
    __metaclass__ = _FormMetaclass

    def __init__(self, **kwargs):
        self.fill(**kwargs)

    def fill(self, **kwargs):
        for k, v in self._fields.iteritems():
            if k in kwargs:
                setattr(self, k, kwargs[k])

    def validate(self):
        errors = {}
        for k, v in self._fields.iteritems():
            error_msg = v.validate(getattr(self, k, None))
            if error_msg:
                errors[k] = error_msg
        return errors

    def _normalize_helper(self, key, descriptor):
        try:
            value = getattr(self, key)
        except AttributeError:
            return descriptor.default
        return descriptor.normalize(value)

    def normalize(self):
        return {k: self._normalize_helper(k, v) for k, v in self._fields.iteritems()}

    def localize(self, *fields, **obj_values):
        def _localize(k, descriptor):
            value = obj_values.get(k)
            setattr(self, k, descriptor.localize(value))
            return getattr(self, k)

        if fields:
            return {k: _localize(k, self._fields[k]) for k in fields}
        return {k: _localize(k, v) for k, v in self._fields.iteritems()}
