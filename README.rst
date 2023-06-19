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



Installation
============

.. code-block:: shell

   pip install wagtail-factories



Usage
=====

Documentation is still in progress, but see the `tests`_ for more examples.

.. _tests: https://github.com/mvantellingen/wagtail-factories/tree/master/tests

.. code-block:: python

    import wagtail_factories
    from . import models


    class MyCarouselItemFactory(wagtail_factories.StructBlockFactory):
        label = 'my-label'
        image = factory.SubFactory(
            wagtail_factories.ImageChooserBlockFactory)

        class Meta:
            model = models.MyBlockItem


    class MyCarouselFactory(wagtail_factories.StructBlockFactory):
        title = "Carousel title"
        items = wagtail_factories.ListBlockFactory(
            MyCarouselItemFactory)

        class Meta:
            model = models.MyCarousel


    class MyTestPageFactory(wagtail_factories.PageFactory):

        body = wagtail_factories.StreamFieldFactory({
            'carousel': MyCarouselFactory
        })

        class Meta:
            model = models.MyTestPage


    def test_my_page():
        root_page = wagtail_factories.PageFactory(parent=None)
        my_page = MyTestPageFactory(
            parent=root_page,
            body__0__carousel__items__0__label='Slide 1',
            body__0__carousel__items__0__image__image__title='Image Slide 1',
            body__0__carousel__items__1__label='Slide 2',
            body__0__carousel__items__1__image__image__title='Image Slide 2',
            body__0__carousel__items__2__label='Slide 3',
            body__0__carousel__items__2__image__image__title='Image Slide 3')

Contributing
============

1. Clone the repo `git clone https://github.com/nhsuk/wagtail-streamfield-index.git`
2. Install dependencies `pip install .[testing,linting]`

If you are having issues in installing, it may be of use to use an environment tool 
like [virtualenv](https://docs.python.org/3/library/venv.html)

Formatting
============

`black .`

Linting
============

`flake8 .`

Tests
============

`pytest`
