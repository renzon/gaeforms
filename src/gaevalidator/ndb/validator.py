# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from google.appengine.ext.ndb.model import IntegerProperty
from gaevalidator.base import IntegerField, Validator, _ValidatorMetaclass

_property_to_field_dct = {}


def registry(property_cls, field_cls):
    _property_to_field_dct[property_cls] = field_cls


registry(IntegerProperty, IntegerField)


class NotRegisteredProperty(Exception):
    pass


class InvalidParams(Exception):
    pass


def extract_names(properties):
    if properties:
        return set(p._code_name for p in properties)


def make_include_function(include, exclude):
    if include and exclude:
        raise InvalidParams('_include and _exclude can not be not None at same time')

    def should_include(key):
        return True

    if include is not None:
        def should_include(key):
            return key in include
    elif exclude is not None:
        def should_include(key):
            return key not in exclude

    return should_include


def set_options(model_property, field):
    field.required = model_property._required
    field.default = model_property._default
    field.repeated = model_property._repeated
    field.choices = model_property._choices
    return field

class _ModelValidatorMetaclass(_ValidatorMetaclass):
    def __new__(cls, class_to_be_created_name, bases, attrs):
        model_class = attrs.get('_model_class')
        if model_class:
            properties = model_class._properties
            include = extract_names(attrs.get('_include'))
            exclude = extract_names(attrs.get('_exclude'))

            should_include = make_include_function(include, exclude)

            for k, v in properties.iteritems():
                if should_include(k):
                    field_class = _property_to_field_dct.get(v.__class__, None)

                    if field_class is None:
                        msg = 'The %s attribute from class %s has a property not registered: %s' % \
                              (k, class_to_be_created_name, v.__class__)
                        raise NotRegisteredProperty(msg)

                    attrs[k] = set_options(v, field_class())
        return super(_ModelValidatorMetaclass, cls).__new__(cls, class_to_be_created_name, bases, attrs)


class ModelValidator(Validator):
    __metaclass__ = _ModelValidatorMetaclass
    _model_class = None
    _include = None
    _exclude = None
