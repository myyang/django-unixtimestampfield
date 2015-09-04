from django.test import TestCase, override_settings

from django.db import models
from django.utils import timezone
from django import forms

from .fields import UnixTimeStampField

unix_0 = timezone.datetime.fromtimestamp(0.0)
unix_0_utc = timezone.datetime.fromtimestamp(0.0, timezone.utc)


class ForTestModel(models.Model):

    created = UnixTimeStampField(auto_now_add=True)
    modified = UnixTimeStampField(auto_now=True)
    str_ini = UnixTimeStampField(default='0.0')
    float_ini = UnixTimeStampField(default=0.0)
    int_ini = UnixTimeStampField(default=0.0)
    dt_ini = UnixTimeStampField(default=unix_0_utc)

    use_numeric_field = UnixTimeStampField(use_numeric=True, default=0.0)
    round_3_field = UnixTimeStampField(use_numeric=True, round_to=3, default=0.0)


class TimeStampFieldTest(TestCase):

    @override_settings(USE_TZ=True, TIME_ZONE='UTC')
    def test_init_with_use_tz(self):
        now = timezone.now()
        expected = timezone.make_aware(timezone.datetime.utcfromtimestamp(0.0), timezone.utc)
        t = ForTestModel.objects.create()

        self.assertGreater(t.created, now)
        self.assertGreater(t.modified, now)
        self.assertEqual(t.str_ini, expected)
        self.assertEqual(t.float_ini, expected)
        self.assertEqual(t.int_ini, expected)

    @override_settings(USE_TZ=True, TIME_ZONE='UTC')
    def test_assignment_with_tz(self):
        expected = timezone.make_aware(timezone.datetime.utcfromtimestamp(3.0), timezone.utc)
        t = ForTestModel.objects.create()

        pre_modified = t.modified

        t.str_ini = '3'
        t.float_ini = 3.0
        t.int_ini = 3
        t.dt_ini = timezone.datetime.fromtimestamp(3.0, timezone.utc)
        t.use_numeric_field = 3.1111116
        t.round_3_field = 3.1116
        t.save()

        if hasattr(t, 'refresh_from_db'):
            t.refresh_from_db()
        else:
            t = ForTestModel.objects.get(id=t.id)

        self.assertGreater(t.modified, pre_modified)
        self.assertEqual(t.str_ini, expected)
        self.assertEqual(t.float_ini, expected)
        self.assertEqual(t.int_ini, expected)
        self.assertEqual(t.use_numeric_field, 3.111112)
        self.assertEqual(t.round_3_field, 3.112)

    @override_settings(USE_TZ=True, TIME_ZONE='Asia/Taipei')
    def test_init_with_different_tz(self):
        now = timezone.now()
        expected = timezone.localtime(
            timezone.make_aware(timezone.datetime.utcfromtimestamp(0.0), timezone.utc),
            timezone.pytz.timezone('Asia/Taipei')
        )
        t = ForTestModel.objects.create()

        self.assertGreater(t.created, now)
        self.assertGreater(t.modified, now)
        self.assertEqual(t.str_ini, expected)
        self.assertEqual(t.float_ini, expected)
        self.assertEqual(t.int_ini, expected)

    @override_settings(USE_TZ=False)
    def test_init_without_tz(self):
        now = timezone.datetime.now()
        expected = timezone.datetime.fromtimestamp(0.0)
        t = ForTestModel.objects.create()

        self.assertGreater(t.created, now)
        self.assertGreater(t.modified, now)
        self.assertEqual(t.str_ini, expected)
        self.assertEqual(t.float_ini, expected)
        self.assertEqual(t.int_ini, expected)

    @override_settings(USE_TZ=False)
    def test_assignment_without_tz(self):
        expected = timezone.datetime.fromtimestamp(3.0)
        t = ForTestModel.objects.create()

        pre_modified = t.modified

        t.str_ini = '3'
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
        self.assertEqual(t.float_ini, expected)
        self.assertEqual(t.int_ini, expected)


class ForTestModelForm(forms.ModelForm):
    class Meta:
        model = ForTestModel
        fields = ['str_ini', 'float_ini', 'int_ini', 'dt_ini',
                  'use_numeric_field', 'round_3_field']


class FormFieldTest(TestCase):

    def test_noraml(self):
        data = {
            'str_ini': '3',
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
        errors = {'str_ini': [u'Enter a number.'], }
        self.assertDictEqual(tform.errors, errors)
        self.assertEqual(tform.error_class, forms.utils.ErrorList)
