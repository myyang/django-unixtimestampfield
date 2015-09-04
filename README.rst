django-unixtimestampfield
===========================

.. image:: https://img.shields.io/travis/myyang/django-unixtimestampfield.svg
         :target: https://travis-ci.org/myyang/django-unixtimestampfield


Provide a custom field that is stored as float and used as datetime instance.


Requirements
------------

* Database that supports **Float** type is compatible
* Python2.7, Python3.4 with Django >= 1.8
  (Since the 1.8 is LTS version, I choose to supports from 1.8. 
  `SubClassing will be removed in 1.10`_ also, so...follow the trends?
  If you could help version < 1.7, it's welcom :D )

.. _`SubClassing will be removed in 1.10`: https://github.com/django/django/blob/1.8/django/db/models/fields/subclassing.py#L21

Install
-------

.. code-block:: shell

   pip install django-unixtimestampfield

**!!! PS**: Not published to `PyPI`_ yet, future work... **!!!**

.. _`PyPI`: https://pypi.python.org/pypi


Usage
-----


Used in model as:

.. code-block:: python

   from django.db import models
   
   from unixtimestampfield.fields import UnixTimeStampField

   class ModelA(models.Model):

        created = UnixTimeStampField(auto_now_add=True)
        modified = UnixTimeStampField(auto_now=True)
        str_ini = UnixTimeStampField(default='0.0')
        float_ini = UnixTimeStampField(default=0.0)
        int_ini = UnixTimeStampField(default=0.0)
        dt_ini = UnixTimeStampField(default=timezone.now)


Behavior exmpale:

.. code-block:: python

    >>> m = modelA.objects.create()
    >>> m.created
    datetime.datetime(2015, 9, 2, 10, 41, 41, 937257, tzinfo=<UTC>)
    >>> m.int_ini
    datetime.datetime(1970, 1, 1, 0, 0, tzinfo=<UTC>)
    >>> m.int_ini = 3
    >>> m.save()
    >>> m.int_ini
    datetime.datetime(1970, 1, 1, 0, 3, tzinfo=<UTC>)

Field Options
~~~~~~~~~~~~~

* **auto_now**: Set as True to refresh while saving, just like DatetimeField
* **auto_now_add**: set as True to add while creating, just like DatetimeField
* **round_to**: percision (*num*)  of round(value, *num*), default: 6
* **use_float**: set as True that instance attribute would be float, default: False

Version
-------

*v0.1* -- Added UnixTimeStampField 
