=================
wagtail-factories
=================

Factory boy classes for Wagtail CMS

.. start-no-pypi

Status
------

.. image:: https://readthedocs.org/projects/wagtail-factories/badge/?version=latest
    :target: https://readthedocs.org/projects/wagtail-factories/
   
.. image:: https://travis-ci.org/mvantellingen/wagtail-factories.svg?branch=master
    :target: https://travis-ci.org/mvantellingen/wagtail-factories


.. image:: https://img.shields.io/pypi/v/wagtail-factories.svg
    :target: https://pypi.python.org/pypi/wagtail-factories/

.. end-no-pypi

Usage
=====
.. code-block:: django


    import wagtail_factories
    from . import models


    class MyTestPageFactory(wagtail_factories.PageFactory):
        class Meta:
            model = models.MyTestPage


    def test_my_page():
        root_page = wagtail_factories.PageFactory()
        my_page = MyTestPageFactory(parent=root_page)

See https://github.com/mvantellingen/wagtail-factories/blob/master/tests/test_factories.py for more examples
