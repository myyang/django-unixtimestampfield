# -*- coding: utf-8 -*-

"""
Sub middleware

release |release|, version |version|

.. versionadded:: 0.3.8

    Bugs fixed: Apply submiddleware to auto_now field and check format in submiddleware

.. versionadded:: 0.3.4

    Add extra function param

.. versionadded:: 0.3.3

    Initial


Contents
--------

Functions:

* :func:`field_value_middleware`

Variables:

* :data:`USF_FORMAT`
* :data:`USF_DATETIME`
* :data:`USF_TIMESTAMP`
* :data:`USF_DEFAULT`

Members
-------

"""
from django.conf import settings

USF_DATETIME, USF_TIMESTAMP, USF_DEFAULT = 'usf_datetime', 'usf_timestamp', 'usf_default'


def get_format():
    usf_format = getattr(settings, 'USF_FORMAT', USF_DEFAULT)
    if usf_format not in [USF_DATETIME, USF_TIMESTAMP, USF_DEFAULT]:
        usf_format = USF_DEFAULT
    return usf_format


USF_FORMAT = get_format()


def field_value_middleware(field, value, usf_format=None):

    if usf_format is None:
        usf_format = get_format()

    if usf_format == USF_DEFAULT:
        return field.to_timestamp(value) if field.use_numeric else field.to_datetime(value)

    if usf_format == USF_DATETIME:
        return field.to_datetime(value)

    if usf_format == USF_TIMESTAMP:
        return field.to_timestamp(value)

    raise ValueError('USF_FORMAT: %s should not in optional values')
