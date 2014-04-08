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


def extract_names(properties):
    if properties:
        return set(p._code_name for p in properties)


class _ModelValidatorMetaclass(_ValidatorMetaclass):
    def __new__(cls, class_to_be_created_name, bases, attrs):
        model_class = attrs.get('_model_class')
        if model_class:
            properties = model_class._properties
            include=extract_names(attrs.get('_include'))
            for k, v in properties.iteritems():
                if include is None or k in include:
                    field_class = _property_to_field_dct.get(v.__class__, None)

                    if field_class is None:
                        msg = 'The %s attribute from class %s has a property not registered: %s' % \
                              (k, class_to_be_created_name, v.__class__)
                        raise NotRegisteredProperty(msg)

                    attrs[k] = field_class()
        return super(_ModelValidatorMetaclass, cls).__new__(cls, class_to_be_created_name, bases, attrs)


class ModelValidator(Validator):
    __metaclass__ = _ModelValidatorMetaclass
    _model_class = None
    _include = None
    _exclude = None
