# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import babel
from babel import dates


def _get_locale():
    return 'en_US'


def _get_tz():
    """
    Factory that returns forms's timezone
    :return:
    """
    return 'UTC'


def locale_factory(factory):
    """
    Decorator which defines a factory function which
    set forms locale. If not defined locale 'en_US' is used

    :param factory: function
    :return: str with locale
    """
    global _get_locale
    _get_locale = factory
    return factory


def tz_factory(factory):
    """
    Decorator which defines a factory function which
    set forms timezone. If not defined tz 'UTC' is used

    :param factory: function
    :return: str: with timezone
    """
    global _get_tz
    _get_tz = factory
    return factory


def get_locale():
    """
    Build a ``babel.Locale`` based on locale factory
    :return: ``babel.Locale``
    """
    return babel.Locale.parse(_get_locale())


def get_timezone():
    """
    Build a ``babel.Timezone`` based on tz factory
    :return: ``babel.Timezone``
    """
    return dates.get_timezone(_get_tz())
