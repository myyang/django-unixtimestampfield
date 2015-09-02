from django.test import TestCase, override_settings

from django.db import models
from django.utils import timezone

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
        t.save()

        t.refresh_from_db()

        self.assertGreater(t.modified, pre_modified)
        self.assertEqual(t.str_ini, expected)
        self.assertEqual(t.float_ini, expected)
        self.assertEqual(t.int_ini, expected)

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

        t.refresh_from_db()

        self.assertGreater(t.modified, pre_modified)
        self.assertEqual(t.str_ini, expected)
        self.assertEqual(t.float_ini, expected)
        self.assertEqual(t.int_ini, expected)
