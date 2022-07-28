=================
wagtail-factories
=================

Factory boy classes for Wagtail CMS

.. start-no-pypi

Status
------

.. image:: https://readthedocs.org/projects/wagtail-factories/badge/?version=latest
    :target: https://readthedocs.org/projects/wagtail-factories/

.. image:: https://github.com/wagtail/wagtail-factories/workflows/Python%20Tests/badge.svg
    :target: https://github.com/wagtail/wagtail-factories/actions?query=workflow%3A%22Python+Tests%22

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

.. _tests: https://github.com/wagtail/wagtail-factories/tree/main/tests

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


    class MyNewsPageFactory(wagtail_factories.PageFactory):
        class Meta:
            model = models.MyNewsPage


    class MyNewsPageChooserBlockFactory(wagtail_factories.PageChooserBlockFactory):
        page = factory.SubFactory(MyNewsPageFactory)


    class MyTestPageFactory(wagtail_factories.PageFactory):
        body = wagtail_factories.StreamFieldFactory({
            'carousel': factory.SubFactory(MyCarouselFactory),
            'news_page': factory.SubFactory(MyNewsPageChooserBlockFactory),
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
            body__0__carousel__items__2__image__image__title='Image Slide 3',
            body__1__news_page__page__title="News",
        )


Using StreamBlockFactory
========================

``StreamBlockFactory`` can be used in conjunction with the other block factory types to create complex, nested ``StreamValues``, much like how ``StreamBlock`` can be used to declare the blocks for a complex ``StreamField``.

First, define your ``StreamBlockFactory`` subclass, using ``factory.SubFactory`` to wrap child block declarations. Be sure to include your ``StreamBlock`` subclass as the model attribute on the inner ``Meta`` class.

.. code-block:: python

    class MyStreamBlockFactory(wagtail_factories.StreamBlockFactory):
        my_struct_block = factory.SubFactory(MyStructBlockFactory)

        class Meta:
            model = MyStreamBlock


Then include your ``StreamBlockFactory`` subclass on a model factory as the argument to a ``StreamFieldFactory``.

.. code-block:: python

    class MyPageFactory(wagtail_factories.PageFactory):
        body = wagtail_factories.StreamFieldFactory(MyStreamBlockFactory)

        class Meta:
            model = MyPage


You can then use a modified version of factory_boy's deep object declaration syntax to build up ``StreamValues`` on the fly.

.. code-block:: python

    MyPageFactory(
        body__0__my_struct_block__some_field="some value",
        body__0__my_struct_block__some_other_field="some other value",
    )


To generate the default value for a block factory, terminate your declaration at the index and provide the block name as the value.

.. code-block:: python

    MyPageFactory(body__0="my_struct_block")


Alternative StreamFieldFactory declaration syntax
=================================================

Prior to version 3.0, ``StreamFieldFactory`` could only be used by providing a dict mapping block names to block factory classes as the single argument, for example:

.. code-block:: python

    class MyTestPageWithStreamFieldFactory(wagtail_factories.PageFactory):
        body = wagtail_factories.StreamFieldFactory(
            {
                "char_array": wagtail_factories.ListBlockFactory(
                    wagtail_factories.CharBlockFactory
                ),
                "int_array": wagtail_factories.ListBlockFactory(
                    wagtail_factories.IntegerBlockFactory
                ),
                "struct": MyBlockFactory,
                "image": wagtail_factories.ImageChooserBlockFactory,
            }
        )
    
        class Meta:
            model = models.MyTestPage
    

This style of declaration is still supported, with the caveat that nested stream blocks are not supported for this approach. From version 3.0, all ``BlockFactory`` values in a ``StreamFieldFactory`` definition of this style *must* be wrapped in factory_boy ``SubFactories``. For example, the above example must be updated to the following for 3.0 compatibility.

.. code-block:: python

    class MyTestPageWithStreamFieldFactory(wagtail_factories.PageFactory):
        body = wagtail_factories.StreamFieldFactory(
            {
                "char_array": wagtail_factories.ListBlockFactory(
                    wagtail_factories.CharBlockFactory
                ),
                "int_array": wagtail_factories.ListBlockFactory(
                    wagtail_factories.IntegerBlockFactory
                ),
                "struct": factory.SubFactory(MyBlockFactory),
                "image": factory.SubFactory(wagtail_factories.ImageChooserBlockFactory),
            }
        )

        class Meta:
            model = models.MyTestPage


This requirement does *not* apply to ``ListBlockFactory``, which is a subclass of ``SubFactory``.
