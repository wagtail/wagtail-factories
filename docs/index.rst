=================
Wagtail Factories
=================

This Django app provides Factory Boy factories for the Wagtail CMS.


Installation
============

.. code-block:: shell

   pip install wagtail-factories



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
