from distutils.core import Command
from setuptools import setup

"""
Copied and stole from https://github.com/bradjasper/django-jsonfield/blob/master/setup.py
"""


class DjangoVerionError(Exception):
    pass


class TestCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from django.conf import settings
        settings.configure(
            DATABASES={
                'default': {'NAME': ':memory:', 'ENGINE': 'django.db.backends.sqlite3'}},
            INSTALLED_APPS=('unixtimestampfield',)
        )
        from django.core.management import call_command
        import django

        if django.VERSION[:2] < (1, 8):
            raise DjangoVerionError("Django version should be at least 1.8")

        if django.VERSION[:2] >= (1, 8):
            django.setup()
        call_command('test', 'unixtimestampfield')

setup(name='django-unixtimestampfield',
      version='0.3.3',
      packages=['unixtimestampfield'],
      license='MIT',
      author='Garfield.Yang',
      author_email='ymy1019@gmail.com',
      url='https://github.com/myyang/django-unixtimestampfield',
      description='Unix timestamp (POSIX type) field',
      long_description=open("README.rst").read(),
      cmdclass={'test': TestCommand},
      install_requires=['django>=1.8',],
      classifiers=[
          'Intended Audience :: Developers',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.4',
          'Framework :: Django',
      ],
      )
