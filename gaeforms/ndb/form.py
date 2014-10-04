# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from google.appengine.ext.ndb.model import IntegerProperty, StringProperty, DateTimeProperty, DateProperty, \
    FloatProperty, TextProperty, BooleanProperty, KeyProperty
from gaeforms.base import IntegerField, Form, _FormMetaclass, DecimalField, StringField, DateField, DateTimeField, \
    FloatField, EmailField, BooleanField, KeyField
from gaeforms.ndb.property import IntegerBounded, SimpleDecimal, SimpleCurrency, FloatBounded, Email

_property_to_field_dct = {}


def registry(property_cls, field_cls):
    _property_to_field_dct[property_cls] = field_cls


registry(IntegerProperty, IntegerField)
registry(IntegerBounded, IntegerField)
registry(SimpleDecimal, DecimalField)
registry(SimpleCurrency, DecimalField)
registry(StringProperty, StringField)
registry(TextProperty, StringField)
registry(DateTimeProperty, DateTimeField)
registry(DateProperty, DateField)
registry(FloatProperty, FloatField)
registry(FloatBounded, FloatField)
registry(Email, EmailField)
registry(BooleanProperty, BooleanField)
registry(KeyProperty, KeyField)


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
        return key != 'class'

    if include is not None:
        def should_include(key):
            return key in include
    elif exclude is not None:
        def should_include(key):
            return key not in exclude and key != 'class'

    return should_include


class _ModelFormMetaclass(_FormMetaclass):
    def __new__(cls, class_to_be_created_name, bases, attrs):
        model_class = attrs.get('_model_class')
        if model_class:
            properties = model_class._properties
            include = extract_names(attrs.get('_include'))
            exclude = extract_names(attrs.get('_exclude'))

            should_include = make_include_function(include, exclude)

            for k, v in properties.iteritems():
                if should_include(k) and k not in attrs:
                    field_class = _property_to_field_dct.get(v.__class__, None)

                    if field_class is None:
                        msg = 'The %s attribute from class %s has a property not registered: %s' % \
                              (k, class_to_be_created_name, v.__class__)
                        raise NotRegisteredProperty(msg)
                    field = field_class()
                    field.set_options(v)
                    attrs[k] = field
        return super(_ModelFormMetaclass, cls).__new__(cls, class_to_be_created_name, bases, attrs)


class ModelFormSecurityError(Exception):
    """
    Exception to raise when an security error ocurs on model form actions
    """
    pass


class ModelForm(Form):
    __metaclass__ = _ModelFormMetaclass
    _model_class = None
    _include = None
    _exclude = None

    def fill_model(self, model=None):
        """
        Populates a model with normalized properties. If no model is provided (None) a new one will be created.
        :param model: model to be populade
        :return: populated model
        """
        normalized_dct = self.normalize()
        if model:
            if not isinstance(model, self._model_class):
                raise ModelFormSecurityError('%s should be %s instance' % (model, self._model_class.__name__))
            model.populate(**normalized_dct)
            return model
        return self._model_class(**normalized_dct)

    def fill_with_model(self, model, *fields):
        """
        Populates this form with localized properties from model.
        :param fields: string list indicating the fields to include. If None, all fields defined on form will be used
        :param model: model
        :return: dict with localized properties
        """
        model_dct = model.to_dict(include=self._fields.keys())
        localized_dct = self.localize(*fields, **model_dct)
        if model.key:
            localized_dct['id'] = model.key.id()
        return localized_dct

