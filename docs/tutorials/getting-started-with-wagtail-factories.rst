======================================
Getting started with wagtail-factories
======================================

Goals
-----

In this tutorial, we will learn how to use the wagtail-factories library to create `factory boy <https://factoryboy.readthedocs.io/en/stable/>`_ factories for a Wagtail project. These factories facilitate the easy creation of model instances, which is particularly useful for tests.

We'll learn about factories for Wagtail's models - factories for stream field blocks will be covered in another document.

We assume working familiarity with Wagtail, and a passing familiarity with factory boy.

Set up a working environment
----------------------------

To follow this tutorial on your own machine, create a new Wagtail project `as described in the Wagtail docs <https://docs.wagtail.org/en/stable/getting_started/tutorial.html#install-and-run-wagtail>`_. The project name doesn't matter - we'll work entirely within the generated ``home`` app.

Page models
-----------

To get started, we'll create some basic page models. Wagtail gives us a ``HomePage`` model by default - we'll keep that.

.. code:: python

    from wagtail.models import Page


    class HomePage(Page):
        pass

Add a ``BlogPage`` type with foreign keys to Wagtail's ``Page``, ``Image``, and ``Document`` models, in ``home/models.py``.

.. code:: python

    from django.db import models
    from wagtail.documents import get_document_model
    from wagtail.images import get_image_model


    class BlogPage(Page):
        hero_image = models.ForeignKey(
            get_image_model(),
            on_delete=models.PROTECT,
            related_name="+",
        )
        splash_text = models.TextField(blank=True)
        related_page = models.ForeignKey(
            Page,
            null=True,
            blank=True,
            on_delete=models.SET_NULL,
            related_name="related_pages",
        )
        policy = models.ForeignKey(
            get_document_model(),
            null=True,
            blank=True,
            on_delete=models.SET_NULL,
            related_name="+",
        )

Create and run the migrations.

.. code:: bash

    python manage.py makemigrations
    python manage.py migrate

With some models created, we are ready to create the corresponding factory classes.

Page factories
--------------

First, we'll create a factory for the ``HomePage`` type in ``home/factories.py``.

.. code:: python

    import factory
    from wagtail_factories import PageFactory

    from home.models import HomePage


    class HomePageFactory(PageFactory):
        class Meta:
            model = HomePage

This one's simple. We can use it to create ``HomePage`` instances:

.. code:: python

    HomePageFactory(title="My temporary home page")

::

    <HomePage: My temporary home page>


Let's also create a ``BlogPageFactory`` with some more declarations in ``home/factories.py``.

.. code:: python

    from wagtail_factories import DocumentFactory, ImageFactory

    from home.models import BlogPage


    class BlogPageFactory(PageFactory):
        hero_image = factory.SubFactory(ImageFactory)
        splash_text = factory.Faker("paragraph")
        related_page = factory.SubFactory(PageFactory)
        policy = factory.SubFactory(DocumentFactory)

        class Meta:
            model = BlogPage

Using our page factories
~~~~~~~~~~~~~~~~~~~~~~~~

Now that we've defined some factories, we can try them out. Generate an instance without any specific parameters and inspect its attributes.

.. code:: python

    blog_page = BlogPageFactory()

    blog_page

::

    <BlogPage: Test page>


A title has been generated.

.. code:: python

    blog_page.title

::

    'Test page'


As has an image...

.. code:: python

    blog_page.hero_image.file

::

    <WagtailImageFieldFile: original_images/example_WGodNWK.jpg>


...a document...

.. code:: python

    blog_page.policy.file

::

    <FieldFile: documents/example_HxlsHjf.dat>


...and text.

.. code:: python

    blog_page.splash_text

::

    ('Type first street surface foot yes. Source national new window improve '
     'church. Just executive forget company almost get some.')


A related page was also generated: we can inspect its attributes.

.. code:: python

    blog_page.related_page.pk

::

    5

More control
~~~~~~~~~~~~

``PageFactory`` subclasses are ultimately ``factory.django.DjangoModelFactory`` subclasses. This means that factory boy's full feature set is available to us, so we can specify the values of our instances, even spanning relationships.


.. code:: python

    blog_2 = BlogPageFactory(
        title="My new blog",
        related_page__title="Closely related page",
        splash_text=factory.LazyAttribute(lambda o: f"{o.related_page.title} is closely related"),
    )

    blog_2.splash_text

::

    'Closely related page is closely related'


See the `factory boy docs <https://factoryboy.readthedocs.io/en/stable/index.html>`_ for all the details.

Image and file details
^^^^^^^^^^^^^^^^^^^^^^

wagtail-factories uses factory boy's `FileField <https://factoryboy.readthedocs.io/en/stable/orms.html#factory.django.FileField>`_ and `ImageField <https://factoryboy.readthedocs.io/en/stable/orms.html#factory.django.ImageField>`_ for its ``DocumentFactory`` and ``ImageFactory``, respectively. As images and documents are important entities in a Content Management System, it may be desirable to control how they are created in our tests.

Using the features provided by factory boy, it is possible to define parameters such as file name and contents for documents.

.. code:: python

    from io import BytesIO
    from wagtail_factories import DocumentFactory


    doc = DocumentFactory(
        file__filename="my-test-doc.txt",
        file__from_file=BytesIO(b"sample content"),
    )

    doc.file.name, doc.file.read()

::

    ('documents/my-test-doc_zdU3J7g.txt', b'sample content')


It may also be desirable to control aspects of generated image files, such as dimensions, colour, and file type.

.. code:: python

    from wagtail_factories import ImageFactory


    image = ImageFactory(
        file__filename="my-image.png",
        file__width=100,
        file__height=25,
        file__format="PNG",
    )

    image.width, image.height

::

    (100, 25)

The page tree
^^^^^^^^^^^^^

In the examples so far, we've shown isolated page instances that don't interact with one of Wagtail's key concepts: the page tree. By default, page instances created via a ``PageFactory`` subclass are not inserted into any existing page tree.

.. code:: python

    BlogPageFactory().get_parent()

::

    None


In practice, we'll often want to replicate a real website's page structure in our tests, for example creating a home page with some children. To mirror a proper Wagtail tree structure, we need a root page, which is an entry in the tree that is not visitable by users, has no parents, and is the ancestor of every page in the tree. This is easy to create using wagtail-factories - in fact, every time we create a page from a factory without an explicit ``parent`` parameter, we are creating one:

.. code:: python

    from wagtail.models import Page


    Page.get_root_nodes()

::

    <PageQuerySet [<Page: Root>, <Page: My temporary home page>, <Page: Test page>, <Page: Test page>, <Page: Closely related page>, <Page: My new blog>, <Page: Test page>, <Page: Test page>]>


However, if we're using Wagtail's provided migrations, `one is provided for us by default <https://github.com/wagtail/wagtail/blob/c78838f6ee89fd8e01101326fa08a36babafd88d/wagtail/migrations/0002_initial_data.py#L17-L25>`_, so we might like to retrieve and use it.

.. code:: python

    root = Page.get_first_root_node()

    home = HomePageFactory(parent=root)

Surprisingly, our home page is still not routable. This is because it does not belong to a ``Site``.

.. code:: python

    home.url, home.get_site()

::

    (None, None)


If we start our project with ``wagtail start``, Wagtail `creates an initial home page instance for us <https://github.com/wagtail/wagtail/blob/c78838f6ee89fd8e01101326fa08a36babafd88d/wagtail/project_template/home/migrations/0002_create_homepage.py#L11-L35>`_. We can use that instance in our tests.

.. code:: python

    from home.models import HomePage


    HomePage.objects.first()

::

    <HomePage: Home>


However, for complete control over the created instances, we can create our own.

.. code:: python

    from wagtail.models import Site


    home = HomePageFactory(
        title="My new home page 2",
        # Use the root page instance created by Wagtail.
        parent=Page.get_first_root_node(),
    )

    # Use the Site instance created by Wagtail.
    site = Site.objects.get(is_default_site=True)

    site.root_page = home
    site.save()

    home.url

::

    '/'


We can then use our new home page as the parent of other pages, e.g. blog pages.

.. code:: python

    blog = BlogPageFactory(parent=home)

    blog.url

::

    '/test-page/'


Whether or not to use Wagtail's default data, or create it all in your test setup, will depend on the specifics of your project.
