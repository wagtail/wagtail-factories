==========
Quickstart
==========

Installation
============

.. code-block:: shell

   pip install wagtail-factories


Usage
=====

.. code-block:: python

    import wagtail_factories
    from wagtail import models as wt_models

    from . import models


    class MyCarouselItemFactory(wagtail_factories.StructBlockFactory):
        label = 'my-label'
        image = factory.SubFactory(wagtail_factories.ImageChooserBlockFactory)

        class Meta:
            model = models.MyBlockItem


    class MyCarouselFactory(wagtail_factories.StructBlockFactory):
        title = "Carousel title"
        items = wagtail_factories.ListBlockFactory(MyCarouselItemFactory)

        class Meta:
            model = models.MyCarousel


    class MyTestPageFactory(wagtail_factories.PageFactory):

        body = wagtail_factories.StreamFieldFactory({
            'carousel': MyCarouselFactory
        })

        class Meta:
            model = models.MyTestPage


    def test_my_page():
        root_page = wt_models.Page.get_first_root_node()
        assert root_page is not None

        my_page = MyTestPageFactory(
            parent=root_page,
            title="My great page",
            body__0__carousel__items__0__label='Slide 1',
            body__0__carousel__items__0__image__image__title='Image Slide 1',
            body__0__carousel__items__1__label='Slide 2',
            body__0__carousel__items__1__image__image__title='Image Slide 2',
            body__0__carousel__items__2__label='Slide 3',
            body__0__carousel__items__2__image__image__title='Image Slide 3',
        )

        # Defaults defined on factory classes are propagated.
        assert my_page.body[0].value["title"] == "Carousel title"

        # Parameters are propagated.
        assert my_page.title == "My great page"
        assert my_page.body[0].value["items"][0].value["label"] == "Slide 1"
