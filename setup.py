from distutils.core import setup
from distutils.core import Command

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

setup(name='django_unixtimestampfield',
      version='0.1',
      packages=['unixtimestampfield'],
      license='MIT',
      include_package_data=True,
      author='Garfield.Yang',
      author_email='ymy1019@gmail.com',
      url='https://github.com/myyang/django-unixtimestampfield',
      description='Unix timestamp (POSIX type) field',
      long_description=open("README.rst").read(),
      install_requires=['Django >= 1.8'],
      tests_require=['Django >= 1.8'],
      cmdclass={'test': TestCommand},
      classifiers=[
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.4',
          'Framework :: Django',
      ],
      )
