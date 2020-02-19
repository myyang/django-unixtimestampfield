try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

from distutils.core import Command

"""
Copied and stole from
1. https://github.com/bradjasper/django-jsonfield/blob/master/setup.py
2. http://stackoverflow.com/a/3851333
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
        from django.apps import apps

        settings.configure(
            DATABASES={
                'default': {
                    'NAME': ':memory:',
                    'ENGINE': 'django.db.backends.sqlite3',
                },
            },
            INSTALLED_APPS=[
                'unixtimestampfield',
            ],
            TEMPLATES=[
                {
                    'BACKEND': 'django.template.backends.django.DjangoTemplates',
                    'DIRS': [],
                    'APP_DIRS': True,
                },
            ]
        )
        apps.populate(settings.INSTALLED_APPS)

        import sys
        from django.test.utils import get_runner

        tr = get_runner(settings)()
        failures = tr.run_tests(['unixtimestampfield', ])
        if failures:
            sys.exit(bool(failures))


setup(name='django-unixtimestampfield',
      version='0.4.0',
      packages=find_packages(),
      license='MIT',
      author='Garfield.Yang',
      author_email='ymy1019@gmail.com',
      url='https://github.com/myyang/django-unixtimestampfield',
      description='Django Unix timestamp (POSIX type) field',
      long_description=open("README.rst").read(),
      cmdclass={'test': TestCommand},
      install_requires=['django>=2.2', 'six>=1.14.0', ],
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: MIT License',
          'Intended Audience :: Developers',
          'Programming Language :: Python',
          'Framework :: Django',
      ],
      )
