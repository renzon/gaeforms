# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from decimal import Decimal
from google.appengine.ext import ndb
from google.appengine.ext.ndb.model import IntegerProperty


class BoundaryError(Exception):
    pass


#this class is used only to distinguish from StringProperty
class Email(ndb.StringProperty):
    pass

class IntegerBounded(ndb.IntegerProperty):
    '''
    Property to define a bounded integer based on lower and upper values
    default value of properties is None and in this case no validation is executed
    '''

    def __init__(self, lower=None, upper=None, **kwargs):
        self.upper = upper
        self.lower = lower
        super(IntegerBounded, self).__init__(**kwargs)

    def _validate(self, value):
        if self.lower is not None and value < self.lower:
            raise BoundaryError('%s is less then %s' % (value, self.lower))
        if self.upper is not None and value > self.upper:
            raise BoundaryError('%s is greater then %s' % (value, self.upper))


class FloatBounded(ndb.FloatProperty):
    '''
    Property to define a bounded Float based on lower and upper values
    default value of properties is None and in this case no validation is executed
    '''

    def __init__(self, lower=None, upper=None, **kwargs):
        self.upper = upper
        self.lower = lower
        super(FloatBounded, self).__init__(**kwargs)

    def _validate(self, value):
        if self.lower is not None and value < self.lower:
            raise BoundaryError('%s is less then %s' % (value, self.lower))
        if self.upper is not None and value > self.upper:
            raise BoundaryError('%s is greater then %s' % (value, self.upper))


class SimpleDecimal(IntegerProperty):
    '''
    Class representing a Decimal. It must be use when decimal places will never change
    decimal_places controls decimal places and its default is 2.
    Ex: decimal_places=2 -> 1.00, decimal_places=3 -> 1.000

    It's representation on db is Integer constructed from it values.
    Ex: decimal_places=2 -> 100, decimal_places=3 -> 1000

    This is useful so queries keep numeric meaning for comparisons like > or <=
    '''

    def __init__(self, decimal_places=2, lower=None, upper=None, **kwargs):
        self.decimal_places = decimal_places
        self.__multipler = (10 ** self.decimal_places)
        self.lower = lower and self._from_base_type(self._to_base_type(lower))
        self.upper = upper and self._from_base_type(self._to_base_type(upper))
        super(SimpleDecimal, self).__init__(**kwargs)

    def _validate(self, value):
        value = self._from_base_type(self._to_base_type(value))
        if self.lower is not None and value < self.lower:
            raise BoundaryError('%s is less then %s' % (value, self.lower))
        if self.upper is not None and value > self.upper:
            raise BoundaryError('%s is greater then %s' % (value, self.upper))
        return value

    def _to_base_type(self, value):
        return int(round(Decimal(value) * self.__multipler))

    def _from_base_type(self, value):
        return Decimal(value) / self.__multipler


class SimpleCurrency(SimpleDecimal):
    def __init__(self, decimal_places=2, lower=0, **kwargs):
        super(SimpleCurrency, self).__init__(decimal_places=decimal_places,
                                             lower=lower,
                                             **kwargs)