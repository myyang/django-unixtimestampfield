import logging

from django.test import TestCase, override_settings

from django.db import models
from django.utils import timezone
from django import forms
from django.core import exceptions
from django.template import Template, Context

from .fields import UnixTimeStampField, OrdinalField, TimestampPatchMixin, OrdinalPatchMixin

unix_0 = timezone.datetime(1970, 1, 1)
unix_0_utc = timezone.datetime(1970, 1, 1, tzinfo=timezone.utc)

ordinal_1 = timezone.datetime.fromordinal(1)
ordinal_1_utc = timezone.make_aware(timezone.datetime.fromordinal(1), timezone.utc)

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class MixinTest(TestCase):

    zero_utc = timezone.datetime(1970, 1, 1, 0, 0,  tzinfo=timezone.utc)
    oneyear_utc = timezone.datetime(
        1971, 1, 1, 1, 1, 1, 123400, tzinfo=timezone.utc)  # 31539661.123400
    oneyear_utc_i = timezone.datetime(1971, 1, 1, 1, 1, 1,  tzinfo=timezone.utc)  # 31539661.0
    zero = timezone.datetime(1970, 1, 1, 0, 0)
    oneyear = timezone.datetime(1971, 1, 1, 1, 1, 1, 123400)
    oneyear_i = timezone.datetime(1971, 1, 1, 1, 1, 1)
    negyear_utc = timezone.datetime(
        1969, 1, 1, 1, 1, 1, 123400, tzinfo=timezone.utc)  # -31532338.8766
    negyear_utc_i = timezone.datetime(1969, 1, 1, 1, 1, 1, tzinfo=timezone.utc)  # -31532339

    @override_settings(USE_TZ=True, TIME_ZONE='UTC')
    def test_to_timestamp_utc(self):
        ts = TimestampPatchMixin()

        self.assertEqual(0, ts.to_timestamp(self.zero_utc))
        self.assertEqual(31539661.123400, ts.to_timestamp(self.oneyear_utc))
        self.assertEqual(31539661, ts.to_timestamp(self.oneyear_utc_i))
        self.assertEqual(-31532338.8766, ts.to_timestamp(self.negyear_utc))
        self.assertEqual(-31532339, ts.to_timestamp(self.negyear_utc_i))

    @override_settings(USE_TZ=True, TIME_ZONE='Asia/Taipei')
    def test_to_timestamp_with_tz(self):
        ts = TimestampPatchMixin()

        self.assertEqual(0, ts.to_timestamp(timezone.localtime(self.zero_utc)))
        self.assertEqual(31539661.123400, ts.to_timestamp(timezone.localtime(self.oneyear_utc)))
        self.assertEqual(31539661, ts.to_timestamp(timezone.localtime(self.oneyear_utc_i)))
        self.assertEqual(-31532338.8766, ts.to_timestamp(timezone.localtime(self.negyear_utc)))
        self.assertEqual(-31532339, ts.to_timestamp(timezone.localtime(self.negyear_utc_i)))

    @override_settings(USE_TZ=False)
    def test_to_timestamp_without_tz(self):
        ts = TimestampPatchMixin()

        self.assertEqual(0, ts.to_timestamp(self.zero_utc))
        self.assertEqual(0, ts.to_timestamp(self.zero))
        self.assertEqual(0, ts.to_timestamp(timezone.localtime(self.zero_utc)))
        self.assertEqual(31539661.123400, ts.to_timestamp(self.oneyear))
        self.assertEqual(31539661.123400, ts.to_timestamp(self.oneyear_utc))
        self.assertEqual(31539661, ts.to_timestamp(self.oneyear_utc_i))
        self.assertEqual(-31532338.8766, ts.to_timestamp(self.negyear_utc))
        self.assertEqual(-31532339, ts.to_timestamp(self.negyear_utc_i))

    @override_settings(USE_TZ=True, TIME_ZONE='UTC')
    def test_to_naive_utc(self):
        ts = TimestampPatchMixin()

        self.assertEqual(self.zero, ts.to_naive_datetime(0))
        self.assertEqual(self.zero, ts.to_naive_datetime(0.0))
        self.assertEqual(self.zero, ts.to_naive_datetime('0'))
        self.assertEqual(self.zero, ts.to_naive_datetime('1970-01-01 00:00:00'))

        self.assertEqual(self.oneyear_i, ts.to_naive_datetime(31539661))
        self.assertEqual(self.oneyear, ts.to_naive_datetime(31539661.123400))
        self.assertEqual(self.oneyear, ts.to_naive_datetime('31539661.123400'))
        self.assertEqual(self.oneyear, ts.to_naive_datetime('1971-01-01 01:01:01.123400'))

    @override_settings(USE_TZ=True, TIME_ZONE='Asia/Taipei')
    def test_to_naive_with_tz(self):
        ts = TimestampPatchMixin()

        self.assertEqual(self.zero, ts.to_naive_datetime(0))
        self.assertEqual(self.zero, ts.to_naive_datetime(0.0))
        self.assertEqual(self.zero, ts.to_naive_datetime('0'))
        self.assertEqual(self.zero, ts.to_naive_datetime('1970-01-01 00:00:00'))

        self.assertEqual(self.oneyear_i, ts.to_naive_datetime(31539661))
        self.assertEqual(self.oneyear, ts.to_naive_datetime(31539661.123400))
        self.assertEqual(self.oneyear, ts.to_naive_datetime('31539661.123400'))
        self.assertEqual(self.oneyear, ts.to_naive_datetime('1971-01-01 01:01:01.123400'))

    @override_settings(USE_TZ=False)
    def test_to_naive_without_tz(self):
        ts = TimestampPatchMixin()

        self.assertEqual(self.zero, ts.to_naive_datetime(0))
        self.assertEqual(self.zero, ts.to_naive_datetime(0.0))
        self.assertEqual(self.zero, ts.to_naive_datetime('0'))
        self.assertEqual(self.zero, ts.to_naive_datetime('1970-01-01 00:00:00'))

        self.assertEqual(self.oneyear_i, ts.to_naive_datetime(31539661))
        self.assertEqual(self.oneyear, ts.to_naive_datetime(31539661.123400))
        self.assertEqual(self.oneyear, ts.to_naive_datetime('31539661.123400'))
        self.assertEqual(self.oneyear, ts.to_naive_datetime('1971-01-01 01:01:01.123400'))

    @override_settings(USE_TZ=True, TIME_ZONE='UTC')
    def test_to_utc_utc(self):
        ts = TimestampPatchMixin()

        self.assertEqual(self.zero_utc, ts.to_utc_datetime(0))
        self.assertEqual(self.zero_utc, ts.to_utc_datetime(0.0))
        self.assertEqual(self.zero_utc, ts.to_utc_datetime('0'))
        self.assertEqual(self.zero_utc, ts.to_utc_datetime('1970-01-01 00:00:00'))

        self.assertEqual(self.oneyear_utc_i, ts.to_utc_datetime(31539661))
        self.assertEqual(self.oneyear_utc, ts.to_utc_datetime(31539661.123400))
        self.assertEqual(self.oneyear_utc, ts.to_utc_datetime('31539661.123400'))
        self.assertEqual(self.oneyear_utc, ts.to_utc_datetime('1971-01-01 01:01:01.123400'))

    @override_settings(USE_TZ=True, TIME_ZONE='Asia/Taipei')
    def test_to_utc_with_tz(self):
        ts = TimestampPatchMixin()

        self.assertEqual(self.zero_utc, ts.to_utc_datetime(0))
        self.assertEqual(self.zero_utc, ts.to_utc_datetime(0.0))
        self.assertEqual(self.zero_utc, ts.to_utc_datetime('0'))
        self.assertEqual(self.zero_utc, ts.to_utc_datetime('1970-01-01 00:00:00'))

        self.assertEqual(self.oneyear_utc_i, ts.to_utc_datetime(31539661))
        self.assertEqual(self.oneyear_utc, ts.to_utc_datetime(31539661.123400))
        self.assertEqual(self.oneyear_utc, ts.to_utc_datetime('31539661.123400'))
        self.assertEqual(self.oneyear_utc, ts.to_utc_datetime('1971-01-01 01:01:01.123400'))

    @override_settings(USE_TZ=False)
    def test_to_utc_without_tz(self):
        ts = TimestampPatchMixin()

        self.assertEqual(self.zero_utc, ts.to_utc_datetime(0))
        self.assertEqual(self.zero_utc, ts.to_utc_datetime(0.0))
        self.assertEqual(self.zero_utc, ts.to_utc_datetime('0'))
        self.assertEqual(self.zero_utc, ts.to_utc_datetime('1970-01-01 00:00:00'))

        self.assertEqual(self.oneyear_utc_i, ts.to_utc_datetime(31539661))
        self.assertEqual(self.oneyear_utc, ts.to_utc_datetime(31539661.123400))
        self.assertEqual(self.oneyear_utc, ts.to_utc_datetime('31539661.123400'))
        self.assertEqual(self.oneyear_utc, ts.to_utc_datetime('1971-01-01 01:01:01.123400'))

    @override_settings(USE_TZ=True, TIME_ZONE='UTC')
    def test_to_datetime_utc(self):
        ts = TimestampPatchMixin()

        self.assertEqual(self.zero_utc, ts.to_datetime(0))
        self.assertEqual(self.zero_utc, ts.to_datetime(0.0))
        self.assertEqual(self.zero_utc, ts.to_datetime('0'))
        self.assertEqual(self.zero_utc, ts.to_datetime('1970-01-01 00:00:00'))

        self.assertEqual(self.oneyear_utc_i, ts.to_datetime(31539661))
        self.assertEqual(self.oneyear_utc, ts.to_datetime(31539661.123400))
        self.assertEqual(self.oneyear_utc, ts.to_datetime('31539661.123400'))
        self.assertEqual(self.oneyear_utc, ts.to_datetime('1971-01-01 01:01:01.123400'))

    @override_settings(USE_TZ=True, TIME_ZONE='Asia/Taipei')
    def test_to_datetime_with_tz(self):
        ts = TimestampPatchMixin()
        zero = timezone.localtime(self.zero_utc)
        oneyear = timezone.localtime(self.oneyear_utc)
        oneyear_i = timezone.localtime(self.oneyear_utc_i)

        self.assertEqual(zero, ts.to_datetime(0))
        self.assertEqual(zero, ts.to_datetime(0.0))
        self.assertEqual(zero, ts.to_datetime('0'))
        self.assertEqual(zero, ts.to_datetime('1970-01-01 00:00:00'))

        self.assertEqual(oneyear_i, ts.to_datetime(31539661))
        self.assertEqual(oneyear, ts.to_datetime(31539661.123400))
        self.assertEqual(oneyear, ts.to_datetime('31539661.123400'))
        self.assertEqual(oneyear, ts.to_datetime('1971-01-01 01:01:01.123400'))

    @override_settings(USE_TZ=False)
    def test_to_datetime_without_tz(self):
        ts = TimestampPatchMixin()

        self.assertEqual(self.zero, ts.to_datetime(0))
        self.assertEqual(self.zero, ts.to_datetime(0.0))
        self.assertEqual(self.zero, ts.to_datetime('0'))
        self.assertEqual(self.zero, ts.to_datetime('1970-01-01 00:00:00'))

        self.assertEqual(self.oneyear_i, ts.to_datetime(31539661))
        self.assertEqual(self.oneyear, ts.to_datetime(31539661.123400))
        self.assertEqual(self.oneyear, ts.to_datetime('31539661.123400'))
        self.assertEqual(self.oneyear, ts.to_datetime('1971-01-01 01:01:01.123400'))

    @override_settings(USE_TZ=True, TIME_ZONE='UTC')
    def test_over_and_under_flow(self):
        ts = TimestampPatchMixin()

        self.assertRaises(exceptions.ValidationError, ts.from_number, 253402272000)
        self.assertRaises(exceptions.ValidationError, ts.from_number, -719163)


class ForTestModel(models.Model):

    created = UnixTimeStampField(auto_now_add=True)
    modified = UnixTimeStampField(auto_now=True)
    str_ini = UnixTimeStampField(default='0.0')
    str_dt_ini = UnixTimeStampField(default='1970-01-01 00:00:00')
    float_ini = UnixTimeStampField(default=0.0)
    int_ini = UnixTimeStampField(default=0.0)
    dt_ini = UnixTimeStampField(default=unix_0_utc)

    use_numeric_field = UnixTimeStampField(use_numeric=True, default=0.0)
    round_3_field = UnixTimeStampField(use_numeric=True, round_to=3, default=0.0)


class TimeStampFieldTest(TestCase):

    @override_settings(USE_TZ=True, TIME_ZONE='UTC')
    def test_init_with_use_tz(self):
        now = timezone.now()
        expected = timezone.datetime(1970, 1, 1, tzinfo=timezone.utc)
        t = ForTestModel.objects.create()

        self.assertGreater(t.created, now)
        self.assertGreater(t.modified, now)
        self.assertEqual(t.str_ini, expected)
        self.assertEqual(t.str_dt_ini, expected)
        self.assertEqual(t.float_ini, expected)
        self.assertEqual(t.int_ini, expected)

    @override_settings(USE_TZ=True, TIME_ZONE='UTC')
    def test_assignment_with_tz(self):
        expected = timezone.datetime(1970, 1, 1, 0, 0, 3, tzinfo=timezone.utc)
        t = ForTestModel.objects.create()

        pre_modified = t.modified

        t.str_ini = '3'
        t.str_dt_ini = '1970-01-01 00:00:03'
        t.float_ini = 3.0
        t.int_ini = 3
        t.dt_ini = timezone.datetime(1970, 1, 1, 0, 0, 3, tzinfo=timezone.utc)
        t.use_numeric_field = 3.1111116
        t.round_3_field = 3.1116
        t.save()

        if hasattr(t, 'refresh_from_db'):
            t.refresh_from_db()
        else:
            t = ForTestModel.objects.get(id=t.id)

        self.assertGreater(t.modified, pre_modified)
        self.assertEqual(t.str_ini, expected)
        self.assertEqual(t.str_dt_ini, expected)
        self.assertEqual(t.float_ini, expected)
        self.assertEqual(t.int_ini, expected)
        self.assertEqual(t.use_numeric_field, 3.111112)
        self.assertEqual(t.round_3_field, 3.112)

    @override_settings(USE_TZ=True, TIME_ZONE='Asia/Taipei')
    def test_init_with_different_tz(self):
        now = timezone.now()
        expected = timezone.localtime(
            timezone.datetime(1970, 1, 1, tzinfo=timezone.utc),
            timezone.pytz.timezone('Asia/Taipei')
        )
        t = ForTestModel.objects.create()

        self.assertGreater(t.created, now)
        self.assertGreater(t.modified, now)
        self.assertEqual(t.str_ini, expected)
        self.assertEqual(t.str_dt_ini, expected)
        self.assertEqual(t.float_ini, expected)
        self.assertEqual(t.int_ini, expected)

    @override_settings(USE_TZ=True, TIME_ZONE='Asia/Taipei')
    def test_assignment_with_different_tz(self):
        expected = timezone.localtime(
            timezone.datetime(1970, 1, 1, 0, 0, 3, tzinfo=timezone.utc),
            timezone.pytz.timezone('Asia/Taipei')
        )

        t = ForTestModel.objects.create()

        pre_modified = t.modified

        t.str_ini = '3'
        t.str_dt_ini = '1970-01-01 00:00:03'
        t.float_ini = 3.0
        t.int_ini = 3
        t.dt_ini = timezone.datetime.fromtimestamp(3.0, timezone.pytz.timezone('Asia/Taipei'))
        t.use_numeric_field = 3.1111116
        t.round_3_field = 3.1116
        t.save()

        if hasattr(t, 'refresh_from_db'):
            t.refresh_from_db()
        else:
            t = ForTestModel.objects.get(id=t.id)

        self.assertGreater(t.modified, pre_modified)
        self.assertEqual(t.str_ini, expected)
        self.assertEqual(t.str_dt_ini, expected)
        self.assertEqual(t.float_ini, expected)
        self.assertEqual(t.int_ini, expected)
        self.assertEqual(t.use_numeric_field, 3.111112)
        self.assertEqual(t.round_3_field, 3.112)

    @override_settings(USE_TZ=False)
    def test_init_without_tz(self):
        now = timezone.datetime.utcnow()
        expected = timezone.datetime(1970, 1, 1, 0, 0)
        t = ForTestModel.objects.create()

        self.assertGreater(t.created, now)
        self.assertGreater(t.modified, now)
        self.assertEqual(t.str_ini, expected)
        self.assertEqual(t.str_dt_ini, expected)
        self.assertEqual(t.float_ini, expected)
        self.assertEqual(t.int_ini, expected)

    @override_settings(USE_TZ=False)
    def test_assignment_without_tz(self):
        expected = timezone.datetime(1970, 1, 1, 0, 0, 3)
        t = ForTestModel.objects.create()

        pre_modified = t.modified

        t.str_ini = '3'
        t.str_dt_ini = '1970-01-01 00:00:03'
        t.float_ini = 3.0
        t.int_ini = 3
        t.dt_ini = timezone.datetime.fromtimestamp(3.0)
        t.save()

        if hasattr(t, 'refresh_from_db'):
            t.refresh_from_db()
        else:
            t = ForTestModel.objects.get(id=t.id)

        self.assertGreater(t.modified, pre_modified)
        self.assertEqual(t.str_ini, expected)
        self.assertEqual(t.str_dt_ini, expected)
        self.assertEqual(t.float_ini, expected)
        self.assertEqual(t.int_ini, expected)

    @override_settings(USE_TZ=False)
    def test_assignment_with_big_num(self):
        expected = timezone.datetime(1970, 1, 1, 0, 0) + timezone.timedelta(seconds=14248491461)
        t = ForTestModel.objects.create()

        pre_modified = t.modified

        t.str_ini = '14248491461'
        t.float_ini = 14248491461.0
        t.int_ini = 14248491461
        t.dt_ini = timezone.datetime.fromtimestamp(14248491461.0)
        t.save()

        if hasattr(t, 'refresh_from_db'):
            t.refresh_from_db()
        else:
            t = ForTestModel.objects.get(id=t.id)

        self.assertGreater(t.modified, pre_modified)
        self.assertEqual(t.str_ini, expected)
        self.assertEqual(t.float_ini, expected)
        self.assertEqual(t.int_ini, expected)

    @override_settings(USE_TZ=False)
    def test_assignment_overflow(self):

        t = ForTestModel.objects.create()
        t.float_ini = 14248491461222.0

        self.assertRaises(exceptions.ValidationError, t.save)


class ForTestModelForm(forms.ModelForm):

    class Meta:
        model = ForTestModel
        fields = ['str_ini', 'float_ini', 'int_ini', 'dt_ini',
                  'use_numeric_field', 'round_3_field']


class FormFieldTest(TestCase):

    def test_noraml(self):
        data = {
            'str_ini': '1999-12-11 10:23:13',
            'float_ini': 3.0,
            'int_ini': 3,
            'dt_ini': 3,
            'use_numeric_field': 0,
            'round_3_field': 0,
        }

        tform = ForTestModelForm(data=data)

        self.assertTrue(tform.is_valid())

    def test_empty_form(self):

        data = {}

        tform = ForTestModelForm(data=data)

        self.assertFalse(tform.is_valid())
        errors = {'dt_ini': [u'This field is required.'],
                  'float_ini': [u'This field is required.'],
                  'int_ini': [u'This field is required.'],
                  'round_3_field': [u'This field is required.'],
                  'str_ini': [u'This field is required.'],
                  'use_numeric_field': [u'This field is required.']}
        self.assertDictEqual(tform.errors, errors)
        self.assertEqual(tform.error_class, forms.utils.ErrorList)

    def test_partial_data(self):

        data = {
            'int_ini': 0,
            'round_3_field': 0,
            'str_ini': '3',
        }

        tform = ForTestModelForm(data=data)

        self.assertFalse(tform.is_valid())
        errors = {'dt_ini': [u'This field is required.'],
                  'float_ini': [u'This field is required.'],
                  'use_numeric_field': [u'This field is required.']}
        self.assertDictEqual(tform.errors, errors)
        self.assertEqual(tform.error_class, forms.utils.ErrorList)

    def test_invalid_data(self):

        data = {
            'str_ini': ['hello'],
            'float_ini': 3.0,
            'int_ini': 3,
            'dt_ini': 3,
            'use_numeric_field': 0,
            'round_3_field': 0,
        }

        tform = ForTestModelForm(data=data)

        self.assertFalse(tform.is_valid())
        errors = {'str_ini': [u"Unable to convert value: '['hello']' to datetime"
                              u", please use 'YYYY-mm-dd HH:MM:SS'"]}
        self.assertDictEqual(tform.errors, errors)
        self.assertEqual(tform.error_class, forms.utils.ErrorList)


class OrdMixinTest(TestCase):

    zero_utc = timezone.datetime(1, 1, 1, 0, 0,  tzinfo=timezone.utc)
    oneyear_utc = timezone.datetime(1, 12, 31, 0, 0, tzinfo=timezone.utc)  # 365
    zero = timezone.datetime(1, 1, 1, 0, 0)
    oneyear = timezone.datetime(1, 12, 31, 0, 0)  # 365

    @override_settings(USE_TZ=True, TIME_ZONE='UTC')
    def test_to_timestamp_utc(self):
        ts = OrdinalPatchMixin()

        self.assertEqual(1, ts.to_timestamp(self.zero_utc))
        self.assertEqual(365, ts.to_timestamp(self.oneyear_utc))

    @override_settings(USE_TZ=True, TIME_ZONE='Asia/Taipei')
    def test_to_timestamp_with_tz(self):
        ts = OrdinalPatchMixin()

        self.assertEqual(1, ts.to_timestamp(timezone.localtime(self.zero_utc)))
        self.assertEqual(365, ts.to_timestamp(timezone.localtime(self.oneyear_utc)))

    @override_settings(USE_TZ=False)
    def test_to_timestamp_without_tz(self):
        ts = OrdinalPatchMixin()

        self.assertEqual(1, ts.to_timestamp(self.zero_utc))
        self.assertEqual(1, ts.to_timestamp(self.zero))
        self.assertEqual(365, ts.to_timestamp(self.oneyear))

    @override_settings(USE_TZ=True, TIME_ZONE='UTC')
    def test_to_naive_utc(self):
        ts = OrdinalPatchMixin()

        self.assertEqual(self.zero, ts.to_naive_datetime(1))
        self.assertEqual(self.zero, ts.to_naive_datetime(1.0))
        self.assertEqual(self.zero, ts.to_naive_datetime('1'))
        self.assertEqual(self.zero, ts.to_naive_datetime('0001-01-01 00:00:00'))

        self.assertEqual(self.oneyear, ts.to_naive_datetime(365))
        self.assertEqual(self.oneyear, ts.to_naive_datetime(365.0))
        self.assertEqual(self.oneyear, ts.to_naive_datetime('365'))
        self.assertEqual(self.oneyear, ts.to_naive_datetime('0001-12-31 00:00:00'))

    @override_settings(USE_TZ=True, TIME_ZONE='Asia/Taipei')
    def test_to_naive_with_tz(self):
        ts = OrdinalPatchMixin()

        self.assertEqual(self.zero, ts.to_naive_datetime(1))
        self.assertEqual(self.zero, ts.to_naive_datetime(1.0))
        self.assertEqual(self.zero, ts.to_naive_datetime('1'))
        self.assertEqual(self.zero, ts.to_naive_datetime('0001-01-01 00:00:00'))

        self.assertEqual(self.oneyear, ts.to_naive_datetime(365))
        self.assertEqual(self.oneyear, ts.to_naive_datetime(365.0))
        self.assertEqual(self.oneyear, ts.to_naive_datetime('365'))
        self.assertEqual(self.oneyear, ts.to_naive_datetime('0001-12-31 00:00:00'))

    @override_settings(USE_TZ=False)
    def test_to_naive_without_tz(self):
        ts = OrdinalPatchMixin()

        self.assertEqual(self.zero, ts.to_naive_datetime(1))
        self.assertEqual(self.zero, ts.to_naive_datetime(1.0))
        self.assertEqual(self.zero, ts.to_naive_datetime('1'))
        self.assertEqual(self.zero, ts.to_naive_datetime('0001-01-01 00:00:00'))

        self.assertEqual(self.oneyear, ts.to_naive_datetime(365))
        self.assertEqual(self.oneyear, ts.to_naive_datetime(365.0))
        self.assertEqual(self.oneyear, ts.to_naive_datetime('365'))
        self.assertEqual(self.oneyear, ts.to_naive_datetime('0001-12-31 00:00:00'))

    @override_settings(USE_TZ=True, TIME_ZONE='UTC')
    def test_to_utc_utc(self):
        ts = OrdinalPatchMixin()

        self.assertEqual(self.zero_utc, ts.to_utc_datetime(1))
        self.assertEqual(self.zero_utc, ts.to_utc_datetime(1.0))
        self.assertEqual(self.zero_utc, ts.to_utc_datetime('1'))
        self.assertEqual(self.zero_utc, ts.to_utc_datetime('0001-01-01 00:00:00'))

        self.assertEqual(self.oneyear_utc, ts.to_utc_datetime(365))
        self.assertEqual(self.oneyear_utc, ts.to_utc_datetime(365.0))
        self.assertEqual(self.oneyear_utc, ts.to_utc_datetime('365'))
        self.assertEqual(self.oneyear_utc, ts.to_utc_datetime('0001-12-31 00:00:00'))

    @override_settings(USE_TZ=True, TIME_ZONE='Asia/Taipei')
    def test_to_utc_with_tz(self):
        ts = OrdinalPatchMixin()

        self.assertEqual(self.zero_utc, ts.to_utc_datetime(1))
        self.assertEqual(self.zero_utc, ts.to_utc_datetime(1.0))
        self.assertEqual(self.zero_utc, ts.to_utc_datetime('1'))
        self.assertEqual(self.zero_utc, ts.to_utc_datetime('0001-01-01 00:00:00'))

        self.assertEqual(self.oneyear_utc, ts.to_utc_datetime(365))
        self.assertEqual(self.oneyear_utc, ts.to_utc_datetime(365.0))
        self.assertEqual(self.oneyear_utc, ts.to_utc_datetime('365'))
        self.assertEqual(self.oneyear_utc, ts.to_utc_datetime('0001-12-31 00:00:00'))

    @override_settings(USE_TZ=False)
    def test_to_utc_without_tz(self):
        ts = OrdinalPatchMixin()

        self.assertEqual(self.zero_utc, ts.to_utc_datetime(1))
        self.assertEqual(self.zero_utc, ts.to_utc_datetime(1.0))
        self.assertEqual(self.zero_utc, ts.to_utc_datetime('1'))
        self.assertEqual(self.zero_utc, ts.to_utc_datetime('0001-01-01 00:00:00'))

        self.assertEqual(self.oneyear_utc, ts.to_utc_datetime(365))
        self.assertEqual(self.oneyear_utc, ts.to_utc_datetime(365.0))
        self.assertEqual(self.oneyear_utc, ts.to_utc_datetime('365'))
        self.assertEqual(self.oneyear_utc, ts.to_utc_datetime('0001-12-31 00:00:00'))

    @override_settings(USE_TZ=True, TIME_ZONE='UTC')
    def test_to_datetime_utc(self):
        ts = OrdinalPatchMixin()

        self.assertEqual(self.zero_utc, ts.to_datetime(1))
        self.assertEqual(self.zero_utc, ts.to_datetime(1.0))
        self.assertEqual(self.zero_utc, ts.to_datetime('1'))
        self.assertEqual(self.zero_utc, ts.to_datetime('0001-01-01 00:00:00'))

        self.assertEqual(self.oneyear_utc, ts.to_datetime(365))
        self.assertEqual(self.oneyear_utc, ts.to_datetime(365.0))
        self.assertEqual(self.oneyear_utc, ts.to_datetime('365'))
        self.assertEqual(self.oneyear_utc, ts.to_datetime('0001-12-31 00:00:00'))

    @override_settings(USE_TZ=True, TIME_ZONE='Asia/Taipei')
    def test_to_datetime_with_tz(self):
        ts = OrdinalPatchMixin()
        zero = timezone.localtime(self.zero_utc)
        oneyear = timezone.localtime(self.oneyear_utc)

        self.assertEqual(zero, ts.to_datetime(1))
        self.assertEqual(zero, ts.to_datetime(1.0))
        self.assertEqual(zero, ts.to_datetime('1'))
        self.assertEqual(zero, ts.to_datetime('0001-01-01 00:00:00'))

        self.assertEqual(oneyear, ts.to_datetime(365))
        self.assertEqual(oneyear, ts.to_datetime(365.0))
        self.assertEqual(oneyear, ts.to_datetime('365'))
        self.assertEqual(oneyear, ts.to_datetime('0001-12-31 00:00:00'))

    @override_settings(USE_TZ=False)
    def test_to_datetime_without_tz(self):
        ts = OrdinalPatchMixin()

        self.assertEqual(self.zero, ts.to_datetime(1))
        self.assertEqual(self.zero, ts.to_datetime(1.0))
        self.assertEqual(self.zero, ts.to_datetime('1'))
        self.assertEqual(self.zero, ts.to_datetime('0001-01-01 00:00:00'))

        self.assertEqual(self.oneyear, ts.to_datetime(365))
        self.assertEqual(self.oneyear, ts.to_datetime(365.0))
        self.assertEqual(self.oneyear, ts.to_datetime('365'))
        self.assertEqual(self.oneyear, ts.to_datetime('0001-12-31 00:00:00'))

    @override_settings(USE_TZ=True, TIME_ZONE='UTC')
    def test_over_and_under_flow(self):
        ts = OrdinalPatchMixin()

        self.assertRaises(exceptions.ValidationError, ts.from_number, 3652060)
        self.assertRaises(exceptions.ValidationError, ts.from_number, 0)
        self.assertRaises(exceptions.ValidationError, ts.from_number, -1)


class ForOrdinalTestModel(models.Model):

    created = OrdinalField(auto_now_add=True)
    modified = OrdinalField(auto_now=True)
    str_ini = OrdinalField(default='1')
    float_ini = OrdinalField(default=1)
    int_ini = OrdinalField(default=1)
    dt_ini = OrdinalField(default=ordinal_1)


class OrdinalFieldTest(TestCase):

    @override_settings(USE_TZ=True, TIME_ZONE='UTC')
    def test_init_with_utc(self):
        today = timezone.make_aware(
            timezone.datetime.fromordinal(timezone.now().toordinal()), timezone.utc)
        expected = timezone.make_aware(timezone.datetime.fromordinal(1), timezone.utc)
        m = ForOrdinalTestModel.objects.create()

        self.assertEqual(m.created, today)
        self.assertEqual(m.modified, today)
        self.assertEqual(m.str_ini, expected)
        self.assertEqual(m.float_ini, expected)
        self.assertEqual(m.int_ini, expected)
        self.assertEqual(m.dt_ini, expected)

    @override_settings(USE_TZ=True, TIME_ZONE='UTC')
    def test_assignment_with_tz(self):
        today = timezone.make_aware(
            timezone.datetime.fromordinal(timezone.now().toordinal()), timezone.utc)
        expected = timezone.make_aware(timezone.datetime.fromordinal(3), timezone.utc)
        m = ForOrdinalTestModel.objects.create()

        m.str_ini = '3'
        m.float_ini = 3.0
        m.int_ini = 3
        m.dt_ini = timezone.make_aware(timezone.datetime.fromordinal(3), timezone.utc)
        m.save()

        if hasattr(m, 'refresh_from_db'):
            m.refresh_from_db()
        else:
            m = ForOrdinalTestModel.objects.get(id=m.id)

        self.assertEqual(m.modified, today)
        self.assertEqual(m.str_ini, expected)
        self.assertEqual(m.float_ini, expected)
        self.assertEqual(m.int_ini, expected)

    @override_settings(USE_TZ=True, TIME_ZONE='Asia/Taipei')
    def test_init_with_different_tz(self):
        today = timezone.make_aware(
            timezone.datetime.fromordinal(timezone.now().toordinal()), timezone.utc)
        expected = timezone.localtime(
            timezone.make_aware(timezone.datetime.fromordinal(1), timezone.utc),
            timezone.pytz.timezone('Asia/Taipei')
        )
        m = ForOrdinalTestModel.objects.create()

        self.assertEqual(m.created, today)
        self.assertEqual(m.modified, today)
        self.assertEqual(m.str_ini, expected)
        self.assertEqual(m.float_ini, expected)
        self.assertEqual(m.int_ini, expected)

    @override_settings(USE_TZ=False)
    def test_init_without_tz(self):
        today = timezone.datetime.fromordinal(timezone.datetime.utcnow().toordinal())
        expected = timezone.datetime.fromordinal(1)
        m = ForOrdinalTestModel.objects.create()

        self.assertEqual(m.created, today)
        self.assertEqual(m.modified, today)
        self.assertEqual(m.str_ini, expected)
        self.assertEqual(m.float_ini, expected)
        self.assertEqual(m.int_ini, expected)

    @override_settings(USE_TZ=False)
    def test_assignment_without_tz(self):

        today = timezone.datetime.fromordinal(timezone.datetime.utcnow().toordinal())
        expected = timezone.datetime.fromordinal(3)
        m = ForOrdinalTestModel.objects.create()

        m.str_ini = '3'
        m.float_ini = 3.0
        m.int_ini = 3
        m.dt_ini = timezone.datetime.fromordinal(3)
        m.save()

        if hasattr(m, 'refresh_from_db'):
            m.refresh_from_db()
        else:
            m = ForOrdinalTestModel.objects.get(id=m.id)

        self.assertEqual(m.modified, today)
        self.assertEqual(m.str_ini, expected)
        self.assertEqual(m.float_ini, expected)
        self.assertEqual(m.int_ini, expected)

    @override_settings(USE_TZ=False)
    def test_assignment_overflow(self):

        t = ForOrdinalTestModel.objects.create()
        t.float_ini = 14248491461222.0

        self.assertRaises(exceptions.ValidationError, t.save)


class TemplateTagsTest(TestCase):

    def setUp(self):
        self.template = Template(
            "{% load unixtimestampfield %} "
            "{{t.str_ini|to_datetime}} "
            "{{t.str_ini|to_timestamp}}"
        )

    @override_settings(USE_TZ=True, TIME_ZONE='UTC')
    def test_render(self):
        t = ForTestModel()
        rendered = self.template.render(Context({'t': t}))
        self.assertIn("Jan. 1, 1970", rendered)
        self.assertIn("0.0", rendered)


class SubmiddlewareModel(models.Model):

    datetime = UnixTimeStampField(default=0.0)
    numeric = UnixTimeStampField(use_numeric=True, default=0.0)


class SubmiddlewareTest(TestCase):

    @override_settings(USE_TZ=True, TIME_ZONE='UTC')
    def test_default(self):
        t = SubmiddlewareModel.objects.create()
        expected = timezone.datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc)

        if hasattr(t, 'refresh_from_db'):
            t.refresh_from_db()
        else:
            t = ForTestModel.objects.get(id=t.id)

        self.assertEqual(t.datetime, expected)
        self.assertEqual(t.numeric, 0)

    @override_settings(USE_TZ=True, TIME_ZONE='UTC', USF_FORMAT='usf_datetime')
    def test_datetime(self):
        t = SubmiddlewareModel.objects.create()
        expected = timezone.datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc)

        self.assertEqual(t.datetime, expected)
        self.assertEqual(t.numeric, expected)

    @override_settings(USE_TZ=True, TIME_ZONE='UTC', USF_FORMAT='usf_timestamp')
    def test_timestamp(self):
        t = SubmiddlewareModel.objects.create()

        self.assertEqual(t.datetime, 0)
        self.assertEqual(t.numeric, 0)

    @override_settings(USE_TZ=True, TIME_ZONE='UTC', USF_FORMAT='invalid')
    def test_invalid_option(self):
        t = SubmiddlewareModel.objects.create()
        expected = timezone.datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc)

        if hasattr(t, 'refresh_from_db'):
            t.refresh_from_db()
        else:
            t = ForTestModel.objects.get(id=t.id)

        self.assertEqual(t.datetime, expected)
        self.assertEqual(t.numeric, 0)
