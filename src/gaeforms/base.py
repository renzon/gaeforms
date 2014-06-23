# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from decimal import Decimal
import datetime
from google.appengine.ext.ndb.model import DateTimeProperty, DateProperty


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
            return '%s should be one of %s' % (self._attr, self.choices)
        if self.default is not None:
            if value is None or value == '':
                value = self.default
        if self.required and (value is None or value == ''):
            return '%s is required' % self._attr


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

    def normalize(self, value):
        """
        Normalizes a value to be stored on db. Transforms string from web requests on db object, removing any
        localization
        :param value: value to be normalize
        :return: a dict with normalized values
        """
        if self.repeated:
            if value:
                return [self.normalize_field(v) for v in value]
            return []
        return self.normalize_field(value)

    def normalize_field(self, value):
        """
        Method that must transform the value from string
        Ex: if the expected type is int, it should return int(self._attr)

        """
        if self.default is not None:
            if value is None or value == '':
                value = self.default
        return value


# Concrete fields
class StringField(BaseField):
    def validate_field(self, value):
        if value and len(value) > 500:
            return '%(attribute)s has %(len)s characters and it must have less than 500' % \
                   {'attribute': self._attr, 'len': len(value)}

        return super(StringField, self).validate_field(value)


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
                    return '%(attribute)s must be greater than %(lower)s' % \
                           {'attribute': self._attr, 'lower': self.lower}
                if self.upper is not None and self.upper < value:
                    return '%(attribute)s must be less than %(upper)s' % \
                           {'attribute': self._attr, 'upper': self.upper}
            return super(IntegerField, self).validate_field(value)
        except:
            return '%(attribute)s must be integer' % {'attribute': self._attr}


    def normalize_field(self, value):
        if value == '':
            value = None
        elif value is not None:
            value = int(value)
        return super(IntegerField, self).normalize_field(value)


class DecimalField(BaseField):
    def __init__(self, required=False, default=None, repeated=False, choices=None, decimal_places=2, lower=None,
                 upper=None):
        super(DecimalField, self).__init__(required, default, repeated, choices)
        self.decimal_places = decimal_places
        self.__multiplier = (10 ** self.decimal_places)
        self.upper = self.normalize_field(upper)
        self.lower = self.normalize_field(lower)

    def set_options(self, model_property):
        super(DecimalField, self).set_options(model_property)
        self.__multiplier = (10 ** model_property.decimal_places)
        self.decimal_places = model_property.decimal_places
        self.lower = self.normalize_field(getattr(model_property, 'lower', None))
        self.upper = self.normalize_field(getattr(model_property, 'upper', None))


    def validate_field(self, value):
        try:
            value = self.normalize_field(value)
            if value is not None:
                if self.lower is not None and self.lower > value:
                    return '%(attribute)s must be greater than %(lower)s' % \
                           {'attribute': self._attr, 'lower': self.lower}
                if self.upper is not None and self.upper < value:
                    return '%(attribute)s must be less than %(upper)s' % \
                           {'attribute': self._attr, 'upper': self.upper}
            return super(DecimalField, self).validate_field(value)
        except:
            return '%(attribute)s must be a number' % {'attribute': self._attr}


    def normalize_field(self, value):
        if value == '':
            value = None
        elif value is not None:
            rounded = int(round(Decimal(value) * self.__multiplier))
            value = Decimal(rounded) / self.__multiplier
        return super(DecimalField, self).normalize_field(value)


class DateField(BaseField):
    def __init__(self, format='%Y/%m/%d', required=False, default=None, repeated=False, choices=None):
        super(DateField, self).__init__(required, default, repeated, choices)
        self.format = format

    def normalize_field(self, value):
        if isinstance(value, basestring):
            return datetime.datetime.strptime(value, self.format)
        return super(DateField, self).normalize_field(value)

    def validate_field(self, value):
        try:
            value = self.normalize_field(value)
            return super(DateField, self).validate_field(value)
        except:
            return '%(attribute)s must be a date' % {'attribute': self._attr}

    def set_options(self, model_property):
        super(DateField, self).set_options(model_property)
        if isinstance(model_property, DateProperty):
            self.format = '%Y/%m/%d'
        elif isinstance(model_property, DateTimeProperty):
            self.format = '%Y/%m/%d %H:%M:%S'


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
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    def validate(self):
        errors = {}
        for k, v in self._fields.iteritems():
            error_msg = v.validate(getattr(self, k, None))
            if error_msg:
                errors[k] = error_msg
        return errors

    def transform(self):
        return {k: v.normalize(getattr(self, k)) for k, v in self._fields.iteritems()}



