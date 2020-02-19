django-unixtimestampfield
===========================

.. image:: https://img.shields.io/travis/myyang/django-unixtimestampfield.svg
         :target: https://travis-ci.org/myyang/django-unixtimestampfield

.. image:: https://img.shields.io/pypi/v/django-unixtimestampfield.svg
         :target: https://pypi.python.org/pypi/django-unixtimestampfield/

.. image:: https://coveralls.io/repos/myyang/django-unixtimestampfield/badge.svg?service=github
        :target: https://coveralls.io/github/myyang/django-unixtimestampfield

Provide a custom field that is stored as float (UTC POSIX timestamp) and used as datetime instance.


Requirements and Compatibility
------------------------------

Database that supports **Float** type is compatible.
  
Currently tested with metrics:

+---------------+-----+-----+-----+-----+
| Django/Python | 3.5 | 3.6 | 3.7 | 3.8 |
+---------------+-----+-----+-----+-----+
| 2.2.x         |  v  |  v  |  v  |     |
+---------------+-----+-----+-----+-----+
| 3.0.x         |     |  v  |  v  |  v  |
+---------------+-----+-----+-----+-----+

* Note: for Python2 and Django1.X, please use v0.3.9 or previous version.


Install
-------

.. code-block:: shell

   pip install django-unixtimestampfield

Usage
-----


Used in model as following:

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
        num_field = UnixTimeStampField(use_numeric=True, default=0.0)


Operation exmpale:

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
    >>> m.num_field
    0.0

Field Options
~~~~~~~~~~~~~

* **auto_now**: Set to True for updating while saving, just like DatetimeField
* **auto_now_add**: set to True for updating while creating, just like DatetimeField
* **round_to**: percision (*num*)  of round(value, *num*), default: **6**
* **use_float**: **DEPRECATED in v0.3**, see use_numeric
* **use_numeric**: set as True that instance attribute would be numeric, default as **False**


Django settings
~~~~~~~~~~~~~~~


If `USE_TZ` is set to `False`, return current datetime (in UTC timezone) info without **tzinfo** while accessing attribute. 

Example:

.. code-block:: python

   # In settings.py
   USE_TZ = False

   >>> m = modelA.objects.create()
   >>> m.created
   datetime.datetime(2015, 9, 2, 10, 41, 41, 937257)

Template Tags
~~~~~~~~~~~~~

Load template tags:

.. code-block:: html

   {% load unixtimestampfield %}


Two django template filter tags are available:

* **to_datetime**: Filter value as datetime
* **to_timestamp**: Filter value as timestamp


Tricky Sub-middleware
~~~~~~~~~~~~~~~~~~~~~

Due to value is stored as float, it's hard for recognizing and leads to this tricky middleware.

Here are 3 modes to show data:

* **usf_default**: Show data by default, according to use_numeric option of field. This is also default setting.
* **usf_datetime**: Always convert to datetime object
* **usf_timestamp**: Always convert to timestamp

Use `USF_FORMAT` to indicate display police in `settings.py`. Let's see examples.

Assume ModelB as:

.. code-block:: python

   class ModelB(models.Model):

        num_field = UnixTimeStampField(use_numeric=True, default=0.0)
        dt_field = UnixTimeStampField(default=0.0)

Then getting field value what you want:

.. code-block:: python

   >>> m = ModelB()
   # with USF_FORMAT='usf_default' in settings.py 
   >>> m.num_field, m.dt_field
   (0.0, datetime.datetime(1970, 1, 1, 0, 0))

   # with USF_FORMAT='usf_datetime' in settings.py 
   >>> m.num_field, m.dt_field
   (datetime.datetime(1970, 1, 1, 0, 0), datetime.datetime(1970, 1, 1, 0, 0))

   # with USF_FORMAT='usf_timestamp' in settings.py 
   >>> m.num_field, m.dt_field
   (0.0, 0.0)


Version
-------

*v0.4.0* -- Fix Python and Django compatiblity, check related section

*v0.3.9* -- Fix packages including in setup.py

*v0.3.8* -- Bugs fixed: Apply submiddleware to auto_now field and check format in submiddleware

*V0.3.7* -- Check minimum value.

*V0.3.6* -- Fix timezone problem. All records are stored UTC timezone and convert while retrive.

*V0.3.5.1* -- Integer compatibility and fix timezone problem

*V0.3.5* -- Parse time format: YYYY-mm-dd HH:MM:SS[.FFFFFF]

*V0.3.4* -- Bugs fixed.

*V0.3.3* -- Add sub-middleware and template tags

*v0.3* -- Add ordinal time field and change field options **use_float** to **use_numeric**!!!

*v0.2* -- Handle formfield and add options while init

*v0.1* -- Added UnixTimeStampField 

LICENSE
-------

MIT
