=================
Wagtail Factories
=================

This Django app provides Factory Boy factories for the Wagtail CMS.

Documentation is still in progress, but see the `tests`_ for more examples.


.. _tests: https://github.com/mvantellingen/wagtail-factories/tree/master/tests


Installation
============

.. code-block:: shell

   pip install wagtail-factories



Usage
=====
.. code-block:: python


    import wagtail_factories
    from . import models


    class MyCarouselItemFactory(wagtail_factories.StructBlockFactory):
        label = 'my-label'
        image = factory.SubFactory((
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
        root_page = wagtail_factories.PageFactory()
        my_page = MyTestPageFactory(
            parent=root_page,
            body__0__carousel__items__0__label='Slide 1',
            body__0__carousel__items__0__image__image__title='Image Slide 1',
            body__0__carousel__items__1__label='Slide 2',
            body__0__carousel__items__1__image__image__title='Image Slide 2',
            body__0__carousel__items__2__label='Slide 3',
            body__0__carousel__items__2__image__image__title='Image Slide 3')
