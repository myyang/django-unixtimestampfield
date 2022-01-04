# encoding: utf-8

"""
UnixTimeStampField

release |release|, version |version|

.. versionadded:: 0.4.0

    Import Six library from https://pypi.org/project/six/.

.. versionadded:: 0.3.7

    Check minimum value.

.. versionadded:: 0.3.6

    Fix timezone problem. All records are stored UTC timezone and convert while retrive.

.. versionadded:: 0.3.5.1

    Integer compatibility and fix timezone problem

.. versionadded:: 0.3.5

    Parse time format: YYYY-mm-dd HH:MM:SS[.FFFFFF]

.. versionadded:: 0.3.4

    Bugs fixed.

.. versionadded:: 0.3.3

    Add sub-middleware and template tags

.. versionadded:: 0.3

    Add ordinal time field and change field options **use_float** to **use_numeric**!!!

.. versionadded:: 0.1

    Initial


Contents
--------

Classes:

* :class:`TimestampPatchMixin`
* :class:`UnixTimeStampField`
* :class:`OrdinalPatchMixin`
* :class:`OrdinalField`

Members
-------

"""
from __future__ import unicode_literals

import datetime

from django.db.models import Field
from django.utils import timezone
from django.core import exceptions
from django.conf import settings
from django.forms import fields

import six

from .submiddleware import field_value_middleware


class TimestampPatchMixin(object):

    INT32 = (1 << 31) - 1
    MAX_TS, MIN_TS = 253402271999.999, -719162  # 9999/12/31 23:59:59, 1/1/1 00:00:00

    def _datetime_to_timestamp(self, v):
        """
        Py2 doesn't supports timestamp()
        """

        # stole from https://docs.python.org/3/library/datetime.html#datetime.datetime.timestamp
        if timezone.is_aware(v):
            return (v - timezone.datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds()
        else:
            return (v - timezone.datetime(1970, 1, 1)).total_seconds()

    def get_datetimenow(self):
        """
        get datetime now according to USE_TZ and default time
        """
        value = timezone.datetime.utcnow()
        if settings.USE_TZ:
            value = timezone.localtime(
                timezone.make_aware(value, timezone.utc),
                timezone.get_default_timezone()
            )
        return value

    def get_timestampnow(self):
        """
        get utc unix timestamp
        """
        return self._datetime_to_timestamp(timezone.datetime.utcnow())

    def to_timestamp(self, value):
        """
        from value to timestamp format(float)
        """
        if isinstance(value, (six.integer_types, float, six.string_types)):
            try:
                return float(value)
            except ValueError:
                value = self.datetime_str_to_datetime(value)

        if isinstance(value, datetime.datetime):
            return self._datetime_to_timestamp(value)

        if value is None:
            try:
                return float(self.default)
            except:
                return 0.0

        raise exceptions.ValidationError(
            "Unable to convert value: '%s' to timestamp" % value,
            code="invalid_timestamp"
        )

    def to_naive_datetime(self, value):
        """
        from value to datetime with tzinfo format (datetime.datetime instance)
        """
        if isinstance(value, (six.integer_types, float, six.string_types)):
            try:
                return self.from_number(value)
            except ValueError:
                return self.datetime_str_to_datetime(value)

        if isinstance(value, datetime.datetime):
            return value

        if value is None:
            try:
                return self.from_number(self.default)
            except:
                return timezone.datetime(1970, 1, 1, 0, 0)

        raise exceptions.ValidationError(
            "Unable to convert value: '%s' to python data type" % value,
            code="invalid_datetime"
        )

    def to_utc_datetime(self, value):
        """
        from value to datetime with tzinfo format (datetime.datetime instance)
        """
        value = self.to_naive_datetime(value)

        if timezone.is_naive(value):
            value = timezone.make_aware(value, timezone.utc)
        else:
            value = timezone.localtime(value, timezone.utc)
        return value

    def to_default_timezone_datetime(self, value):
        """
        convert to default timezone datetime
        """
        return timezone.localtime(self.to_utc_datetime(value), timezone.get_default_timezone())

    def to_datetime(self, value):

        if settings.USE_TZ:
            if settings.TIME_ZONE != 'UTC':
                return self.to_default_timezone_datetime(value)
            else:
                return self.to_utc_datetime(value)
        else:
            return self.to_naive_datetime(value)

    def datetime_str_to_datetime(self, value):
        try:
            if value.find('.') >= 0:
                return timezone.datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')
            else:
                return timezone.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        except:
            raise exceptions.ValidationError(
                "Unable to convert value: '%s' to datetime, "
                "please use 'YYYY-mm-dd HH:MM:SS'" % value,
                code="invalid_timestamp"
            )

    def from_number(self, value):
        value = float(value)
        if value > self.MAX_TS or value < self.MIN_TS:
            raise exceptions.ValidationError(
                "Value out of range,acceptable: "
                "%s ~ %s (1/1/1 00:00:00 ~ 9999/12/31 23:59:59)" % (self.MIN_TS, self.MAX_TS),
                code="out_of_rnage"
            )

        return timezone.datetime(1970, 1, 1, 0, 0) + timezone.timedelta(seconds=value)


class UnixTimeStampField(TimestampPatchMixin, Field):
    """
    Copy and mimic django.db.models.fields.DatetimeField
    Stored as float in database and used as datetime object in Python

    """
    empty_strings_allowed = False
    description = "Unix POSIX timestamp"

    def __init__(self, verbose_name=None, name=None, auto_now=False,
                 auto_now_add=False, round_to=6, use_numeric=False, **kwargs):
        self.auto_now, self.auto_now_add = auto_now, auto_now_add
        self.round_to, self.use_numeric = round_to, use_numeric
        if auto_now or auto_now_add:
            kwargs['editable'] = False
            kwargs['blank'] = True
        super(UnixTimeStampField, self).__init__(verbose_name, name, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(UnixTimeStampField, self).deconstruct()
        if self.auto_now:
            kwargs['auto_now'] = True
        if self.auto_now_add:
            kwargs['auto_now_add'] = True
        if self.auto_now or self.auto_now_add:
            del kwargs['editable']
            del kwargs['blank']
        return name, path, args, kwargs

    def get_internal_type(self):
        return "FloatField"

    def pre_save(self, model_instance, add):
        if self.auto_now or (self.auto_now_add and add):
            value = self.get_datetimenow()
        else:
            value = getattr(model_instance, self.attname)

        setattr(model_instance, self.attname, field_value_middleware(self, value))
        return value

    def to_python(self, value):
        return field_value_middleware(self, value)

    def get_default(self):
        if self.auto_now or self.auto_now_add:
            v = self.get_datetimenow()
        else:
            v = 0.0

        if self.has_default():
            v = self.default
            if callable(self.default):
                v = self.default()
        return self.to_python(v)

    def value_to_string(self, obj):
        val = self._get_val_from_obj(obj)
        return '' if val is None else val

    def get_prep_value(self, value):
        value = super(UnixTimeStampField, self).get_prep_value(value)
        return self.to_timestamp(value)

    def get_db_prep_value(self, value, connection, prepared=False):
        if not prepared:
            value = self.get_prep_value(value)
        return self.to_timestamp(value)

    def from_db_value(self, value, expression, connection):
        return field_value_middleware(self, value)

    def to_timestamp(self, value):
        return round(super(UnixTimeStampField, self).to_timestamp(value), self.round_to)

    def formfield(self, **kwargs):
        defaults = {'form_class': fields.CharField}
        defaults.update(kwargs)
        return super(UnixTimeStampField, self).formfield(**defaults)


class OrdinalPatchMixin(TimestampPatchMixin):

    MAX_OD = 3652059  # 9999/12/31

    def _datetime_to_timestamp(self, v):
        """
        overwrite to use toordinal
        """
        return v.toordinal()

    def get_datetimenow(self):
        """
        get datetime now according to USE_TZ and default time
        """
        value = timezone.datetime.fromordinal(timezone.datetime.utcnow().toordinal())
        if settings.USE_TZ:
            value = timezone.localtime(
                timezone.make_aware(value, timezone.utc),
                timezone.get_default_timezone()
            )
        return value

    def to_timestamp(self, value):
        """
        from value to ordinal timestamp format(int)
        """
        if isinstance(value, (six.integer_types, float, six.string_types)):
            try:
                return int(value)
            except ValueError:
                value = self.datetime_str_to_datetime(value)

        if isinstance(value, datetime.datetime):
            if timezone.is_aware(value):
                value = timezone.localtime(value, timezone.utc)
            return self._datetime_to_timestamp(value)

        raise exceptions.ValidationError(
            "Unable to convert value: '%s' to timestamp" % value,
            code="invalid_timestamp"
        )

    def to_naive_datetime(self, value):
        """
        from value to datetime with tzinfo format (datetime.datetime instance)
        """
        if isinstance(value, (six.integer_types, float, six.string_types)):
            try:
                return self.from_number(value)
            except ValueError:
                return self.datetime_str_to_datetime(value)

        if isinstance(value, datetime.datetime):
            return value

        raise exceptions.ValidationError(
            "Unable to convert value: '%s' to python data type" % value,
            code="invalid_datetime"
        )

    def to_utc_datetime(self, value):
        """
        from value to datetime with tzinfo format (datetime.datetime instance)
        """
        if isinstance(value, (six.integer_types, float, six.string_types)):
            value = self.to_naive_datetime(value)

        if isinstance(value, datetime.datetime):
            if timezone.is_naive(value):
                value = timezone.make_aware(value, timezone.utc)
            else:
                value = timezone.localtime(value, timezone.utc)
            return value

        raise exceptions.ValidationError(
            "Unable to convert value: '%s' to python data type" % value,
            code="invalid_datetime"
        )

    def from_number(self, value):
        value = int(value)
        if value > self.MAX_OD or value < 1:
            raise exceptions.ValidationError(
                "Value out of range, acceptable: 1 ~ %s (1/1/1 ~ 9999/12/31)" % self.MAX_OD,
                code="out_of_rnage"
            )
        return timezone.datetime(1, 1, 1, 0, 0) + timezone.timedelta(days=(value-1))


class OrdinalField(OrdinalPatchMixin, UnixTimeStampField):
    """
    Copy and mimic django.db.models.fields.DatetimeField
    Stored as float in database and used as datetime object in Python

    """
    empty_strings_allowed = False
    description = "Ordinal timestamp"

    def __init__(self, verbose_name=None, name=None, auto_now=False,
                 auto_now_add=False, use_numeric=False, **kwargs):
        self.auto_now, self.auto_now_add, self.use_numeric = auto_now, auto_now_add, use_numeric
        if auto_now or auto_now_add:
            kwargs['editable'] = False
            kwargs['blank'] = True
        super(UnixTimeStampField, self).__init__(verbose_name, name, **kwargs)

    def get_internal_type(self):
        return "FloatField"

    def formfield(self, **kwargs):
        defaults = {'form_class': fields.CharField}
        defaults.update(kwargs)
        return super(OrdinalField, self).formfield(**defaults)
