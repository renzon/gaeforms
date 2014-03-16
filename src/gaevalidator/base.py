# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals


class FieldBase(object):
    def __init__(self, required=False, default=None, repeated=False, choices=None):
        self.repeated = repeated
        self.choices = choices
        self.default = default
        self.required = required
        self._attr = ''


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
            value = self.transform_field(value)
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

    def transform(self, value):
        if self.repeated:
            if value:
                return [self.transform_field(v) for v in value]
            return []
        return self.transform_field(value)

    def transform_field(self, value):
        '''
        Method that must transform the value from string
        Ex: if the expected type is int, it should return int(self._attr)
        '''
        if self.default is not None:
            if value is None or value == '':
                value = self.default
        return value


class _ValidatorMetaclass(type):
    def __new__(cls, attr_name, bases, attrs):
        def set_descriptor_attr_name(descriptor, name):
            descriptor._set_attr_name(name)
            return descriptor

        descriptors = (set_descriptor_attr_name(attr_value, attr_name)
                       for attr_name, attr_value in attrs.iteritems()
                       if hasattr(attr_value, '_set_attr_name'))

        attrs['_fields'] = {d._attr: d for d in descriptors}

        return super(_ValidatorMetaclass, cls).__new__(cls, attr_name, bases, attrs)


class Validator(object):
    _fields = ()
    __metaclass__ = _ValidatorMetaclass

    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    def validate(self):
        errors = {}
        for k, v in self._fields.iteritems():
            error_msg = v.validate(getattr(self, k))
            if error_msg:
                errors[k] = error_msg
        return errors

    def transform(self):
        return {k: v.transform(getattr(self, k)) for k, v in self._fields.iteritems()}



