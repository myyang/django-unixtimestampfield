django-unixtimestampfield
===========================

.. image:: https://img.shields.io/travis/myyang/django-unixtimestampfield.svg
         :target: https://travis-ci.org/myyang/django-unixtimestampfield


Provide a custom field that is stored as float and used as datetime instance.

* Database that supports **Float** type is compatible

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



Version
-------

*v0.1* -- Added UnixTimeStampField 
