|django-factory-generator v1.0.4 on PyPi| |MIT license| |Stable|

django-factory-generator
========================

Generate (factory_boy) Model Factory for each model of your Django app

Changelog
---------

-  1.0.4 fix has_choices property for Django 3.0
-  1.0.3 Remove useless print statements
-  1.0.2 Add ``PointFieldFaker`` to support ``PointField``. Refactor the
   way modules are imported on generated factories
-  1.0.1 Add more accurate fakers for ``BigIntegerField``,
   ``IntegerField``, ``PositiveIntegerField``,
   ``PositiveSmallIntegerField`` and ``SmallIntegerField``
-  1.0.0 Init project

Requirements
------------

This Django app generates factory_boy Model Factories from your
installed apps, so you need to have
`factory_boy <https://github.com/FactoryBoy/factory_boy>`__ installed.

Installation
------------

Install using ``pip`` :

``pip install django_factory_generator``

Add ``factory_generator`` to your ``INSTALLED_APPS`` settings.

.. code:: python

   INSTALLED_APPS = (
       ...
       'factory_generator',
       ...
   )

Generate factories
------------------

Generate factories with a single command line:

``python manage.py generate_factories``

This will create a ``model_factories`` directory with the following
structure :

::

   |__ model_factories/
       |__ app_label_foo/
           |__ __init__.py
           |__ model_foo.py
           |__ model_bar.py
           |__ base/
               |__ __init__.py
               |__ model_foo.py
               |__ model_bar.py

Each model results in two generated files :

-  *model_factories/app_label_foo/base/model_foo* containing the
   ``ModelFooFactoryBase`` class definition generated from the model
   ``ModelFoo``. This file **should not be manually edited** since it
   would be overriden each time the command ``generate_factories`` is
   run.
-  *model_factories/app_label_foo/model_foo* containing the
   ``ModelFooFactory`` class which simply extends
   ``ModelFooFactoryBase``. This file is generated once but not
   overriden when you run the ``generate_factories`` command again.

This structure gives you the ability to **override** the ModelFactory
that was automatically generated. You can then edit the
``ModelFooFactory`` to change / edit the base fields that were
generated.

You can then import your model factories the following way:

::

   # app_label/tests.py
   from django.test import TestCase

   from model_factories.app_label import ModelFooFactory, ModelBarFactory

   class FooTests(TestCase):

       def test_model_factory(self):
           modelfoo = ModelFooFactory(
               foo='bar',
           )
           modelbar = ModelBarFactory(
               bar='baz',
           )
           # Run your tests here

Settings
--------

Here are all the settings you can use, with their default value :

::

   FACTORY_NORMALIZE_FIELD_MAP = {}
   FACTORY_FIELD_FAKER_MAP = {}
   FACTORY_IGNORE_FIELDS = []
   FACTORY_ROOT_DIR = 'model_factories'
   FACTORY_IGNORE_NON_EDITABLE_FIELDS = True

Todo
----

-  Improve documentation
-  Write unit tests
-  validate compatibility with previous versions of Django and Python

Support
-------

If you are having issues, please let us know or submit a pull request.

License
-------

The project is licensed under the MIT License.

.. |django-factory-generator v1.0.4 on PyPi| image:: https://img.shields.io/badge/pypi-1.0.4-green.svg
   :target: https://pypi.python.org/pypi/django-factory-generator
.. |MIT license| image:: https://img.shields.io/badge/licence-MIT-blue.svg
.. |Stable| image:: https://img.shields.io/badge/status-stable-green.svg

