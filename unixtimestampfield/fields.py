# encoding: utf-8

"""
UnixTimeStampField

release |release|, version |version|

.. versionadded:: 1.0

    Initial

Contents
--------

Classes:

* :class:`TimestampPatchMixin`
* :class:`UnixTimeStampField`
* :class:`OrdinalPatchMixin`
* :class:`OrdinalField`

Functions:

Variables:

Members
-------

"""

import time
import datetime

from django.db.models import Field
from django.utils import timezone
from django.core import exceptions
from django.conf import settings
from django.forms import fields

from django.utils.translation import ugettext_lazy as _

from .submiddleware import field_value_middleware


class TimestampPatchMixin(object):

    def _datetime_to_timestamp(self, v):
        """
        Py2 doesn't supports timestamp()
        """

        if hasattr(v, 'timestamp'):
            return v.timestamp()

        return time.mktime(v.timetuple()) + v.microsecond * 0.00001

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
        if isinstance(value, str) or isinstance(value, int) or isinstance(value, float):
            return float(value)
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
        if isinstance(value, str) or isinstance(value, int) or isinstance(value, float):
            value = timezone.datetime.fromtimestamp(float(value))
            return value

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
        if isinstance(value, str) or isinstance(value, int) or isinstance(value, float):
            value = timezone.datetime.fromtimestamp(float(value), timezone.utc)
            return value

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


class UnixTimeStampField(TimestampPatchMixin, Field):
    """
    Copy and mimic django.db.models.fields.DatetimeField
    Stored as float in database and used as datetime object in Python

    """
    empty_strings_allowed = False
    description = _("Unix POSIX timestamp")

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
            setattr(model_instance, self.attname, value)
            return value
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

    def from_db_value(self, value, expression, connection, context):
        return field_value_middleware(self, value)

    def to_timestamp(self, value):
        return round(super(UnixTimeStampField, self).to_timestamp(value), self.round_to)

    def formfield(self, **kwargs):
        defaults = {'form_class': fields.FloatField}
        defaults.update(kwargs)
        return super(UnixTimeStampField, self).formfield(**defaults)


class OrdinalPatchMixin(TimestampPatchMixin):

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
        if isinstance(value, str) or isinstance(value, int) or isinstance(value, float):
            value = int(value)
            if value > 0:
                return value
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
        if isinstance(value, str) or isinstance(value, int) or isinstance(value, float):
            value = timezone.datetime.fromordinal(int(value))
            return value

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
        if isinstance(value, str) or isinstance(value, int) or isinstance(value, float):
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


class OrdinalField(OrdinalPatchMixin, UnixTimeStampField):
    """
    Copy and mimic django.db.models.fields.DatetimeField
    Stored as float in database and used as datetime object in Python

    """
    empty_strings_allowed = False
    description = _("Ordinal timestamp")

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
        defaults = {'form_class': fields.IntegerField}
        defaults.update(kwargs)
        return super(OrdinalField, self).formfield(**defaults)
