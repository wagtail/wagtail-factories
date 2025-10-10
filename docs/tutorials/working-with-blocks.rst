===================
Working with blocks
===================

Goals
-----

Wagtail's killer feature is the `stream field system for flexible content <https://docs.wagtail.org/en/stable/topics/streamfield.html>`_. In this tutorial we will learn how to create and use factory classes that enable us to generate content for stream field blocks, just like we would with factories for Django models.

We assume a working knowledge of Wagtail and a passing knowledge of `factory boy <https://factoryboy.readthedocs.io/en/stable/>`_. This tutorial also assumes you've read `the getting started tutorial <getting-started.rst>`_, and have a Wagtail project with the structures, models, and factories as defined there.

Defining stream field blocks
----------------------------

Before creating any factories, we will create a Django model with a stream field and a set of blocks that define its content model. Create the following model for a fictional animal charity in ``home/models.py``.

.. code:: python

    from wagtail.fields import StreamField
    from wagtail.models import Page

    from home.blocks import PetsBlock


    class PetPage(Page):
        pets = StreamField(PetsBlock())

We need to define ``PetsBlock``, so create it and its sub-blocks in ``home/blocks.py``.

.. code:: python

    from wagtail import blocks
    from wagtail.images.blocks import ImageBlock


    def get_colour_choices():
        return [
            ("calico", "Calico"),
            ("tabby", "Tabby"),
            ("orange", "Orange"),
            ("tortoiseshell", "Tortoiseshell"),
        ]


    class ScheduledFeedingBlock(blocks.StructBlock):
        time = blocks.TimeBlock()
        portions = blocks.IntegerBlock()
        food = blocks.CharBlock()


    class PetStoryBlock(blocks.StreamBlock):
        text = blocks.TextBlock()
        link = blocks.URLBlock()
        image = ImageBlock()


    class PetBlock(blocks.StructBlock):
        story = PetStoryBlock()
        name = blocks.CharBlock()
        date_of_birth = blocks.DateBlock()
        feeding_schedule = blocks.ListBlock(ScheduledFeedingBlock())
        colour = blocks.ChoiceBlock(choices=get_colour_choices)
        picture = ImageBlock()


    class CatBlock(PetBlock):
        pass


    class DogBlock(PetBlock):
        pass


    class PetsBlock(blocks.StreamBlock):
        cat = CatBlock()
        dog = DogBlock()

The block definition contains a variety of structures:

- stream blocks (``PetsBlock``, ``PetBlock.story``);

- a list block;

- struct blocks;

- image blocks;

- choice blocks; and

- various other atomic block types.

Create and run the migrations.

.. code:: bash

    python manage.py makemigrations
    python manage.py migrate

Block factories
---------------

With our model and block definitions in place, it's time to create our block factories. wagtail-factories provides us with the following tools:

- ``StreamBlockFactory``;

- ``StreamFieldFactory``;

- ``ListBlockFactory``;

- ``StructBlockFactory``;

- ``PageChooserBlockFactory``;

- ``ImageChooserBlockFactory``;

- ``DocumentChooserBlockFactory``;

- ``ImageBlockFactory``; and

- some factories atomic block types, although as we'll see they aren't as essential as the factories for compound block types.

Creating factories for our block types, like we would for ``Page`` classes or other Django models, will help us to easily create meaningful values for tests and placeholder content.

We'll start with the bottom of the tree, a factory for ``ScheduledFeedingBlock``.

Factories for struct blocks
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add the following code to ``home/factories.py``.

.. code:: python

    import factory
    from wagtail_factories import StructBlockFactory

    from home.blocks import ScheduledFeedingBlock


    class ScheduledFeedingBlockFactory(StructBlockFactory):
        time = factory.Faker("time_object")
        portions = factory.Faker("random_int", min=1, max=100)
        food = factory.Faker(
            "random_element", elements=["kibble", "tuna", "salmon", "carrots"]
        )

        class Meta:
            model = ScheduledFeedingBlock

We have:

- created a ``StructBlockFactory`` subclass for our ``StructBlock`` subclass;

- added one declaration for each field on the block definition; and

- added an inner ``Meta`` class with a ``model`` attribute which is the corresponding block class.

The ``Meta.model`` declaration is essential: wagtail-factories needs this to create values of the correct type. It should be the relevant block class.

In this example, we're using the API exposed by ``factory.Faker``. This helps us to generate reasonable-looking defaults for fields we don't specify explicit values for when creating block instances.

.. code:: python

    import home.factories as f


    f.ScheduledFeedingBlockFactory()

::

    StructValue([('time', datetime.time(23, 44, 20, 394650)),
                 ('portions', 91),
                 ('food', 'kibble')])


We can also specify values for some or all of the fields.

.. code:: python

    f.ScheduledFeedingBlockFactory(
        portions=3,
        food="kibble",
    )

::

    StructValue([('time', datetime.time(0, 55, 43, 57250)),
                 ('portions', 3),
                 ('food', 'kibble')])


In the next section, we'll learn how to create and use factories for another of Wagtail's compound block types: ``StreamBlock``.

Stream block factories
~~~~~~~~~~~~~~~~~~~~~~

Looking back at the definition of ``PetBlock``, we can see that it contains a stream block definition.

.. code:: python

    class PetStoryBlock(blocks.StreamBlock):
        text = blocks.TextBlock()
        link = blocks.URLBlock()
        image = ImageBlock()


    class PetBlock(blocks.StructBlock):
        ...
        story = PetStoryBlock()
        ...

Create a factory for ``PetStoryBlock`` in ``home/factories.py``. We'll use faker instances for the atomic fields, and a ``SubFactory`` for the nested ``ImageBlock``.

.. code:: python

    import factory
    from wagtail_factories import ImageBlockFactory, StreamBlockFactory

    from home.blocks import PetStoryBlock


    class PetStoryBlockFactory(StreamBlockFactory):
        image = factory.SubFactory(ImageBlockFactory)
        text = factory.Faker("sentence")
        link = factory.Faker("uri")

        class Meta:
            model = PetStoryBlock

Again, note the inner ``Meta`` class with ``model`` definition - this is required.

Using a stream block factory
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Let's try using our new stream block value to generate a value.

.. code:: python

    f.PetStoryBlockFactory()

::

    <StreamValue []>


With no parameters, an empty ``StreamValue`` is generated.

Given that a ``StreamValue`` is an ordered sequence type, how do we specify values for its elements? wagtail-factories supports a syntax for declaring parameters that includes indices for list block and stream block factories. For stream block factories, that syntax comes in two flavours:

1. a "default value" flavour; and

2. a "specified value" flavour.

The default value flavour looks like this:

::

    <index>=<block name string>

So, to create an instance of ``PetStoryBlock`` where the first element is a text block, we would do the following:

.. code:: python

    f.PetStoryBlockFactory(**{"0": "text"})

::

    <StreamValue [<block text: 'Hit into field political stuff.'>]>


This creates a block instance at index 0 using a default value as provided by the ``text`` declaration on ``PetStoryBlockFactory``.

Ideally, we wouldn't need the dict-unpacking to insert the keyword-argument parameters, but Python identifiers cannot begin with a numeric character. This will not be an issue when used in the context of a page (or other containing model), as you'll see in later examples.

The syntax for the "specified value" flavour looks like this:

::

    <index>__<block name>=<value>

For example:

.. code:: python

    f.PetStoryBlockFactory(**{"0__text": "hello"})

::

    <StreamValue [<block text: 'hello'>]>


This lets us specify the position of the block in the stream, the type of block, and its value. We can combine these two syntaxes arbitrarily, and create streams with multiple elements:

.. code:: python

    f.PetStoryBlockFactory(**{"0__text": "hello", "1": "link", "2": "text"})

::

    <StreamValue [<block text: 'hello'>, <block link: 'http://www.vaughn.com/tags/categorymain.htm'>, <block text: 'Game project play box college course.'>]>


However, indices *must* start at zero, and *must* be sequential.

.. code:: python

    f.PetStoryBlockFactory(**{"0": "link", "7": "link"})

::

    wagtail_factories.builder.InvalidDeclaration:
      Parameters for <PetStoryBlockFactory for <class 'home.blocks.PetStoryBlock'>>
      missing required index 1

We can also use double-underscores to traverse the block definition tree, and specify values for nested compound blocks, such as the image block option in ``PetStoryBlock``.

.. code:: python

    with_image = f.PetStoryBlockFactory(**{"0__image__decorative": True})
    with_image[0].value.decorative

::

    True


This declaration can be read as:

::

    <index>__<block name>__<block field>=<value>

To specify multiple values for a particular nested block, we can add declarations with the same ``<index>__<block_name>`` prefix.

.. code:: python

    with_image = f.PetStoryBlockFactory(
        **{
            "0__image__decorative": False,
            "0__image__alt_text": "An orange cat lying in the sun",
            "0__image__image__image__file__color": "orange",
        }
    )

    with_image[0].value.decorative, with_image[0].value.contextual_alt_text

::

    (False, 'An orange cat lying in the sun')

Factories for list blocks
~~~~~~~~~~~~~~~~~~~~~~~~~

With the nested factory definitions taken care of, we can now create a factory for our ``PetBlock``.

.. code:: python

    from wagtail_factories import (
        CharBlockFactory,
        ListBlockFactory,
        PageFactory,
        StreamFieldFactory,
    )
    from home.blocks import PetBlock, get_colour_choices


    class PetBlockFactory(StructBlockFactory):
        story = StreamFieldFactory(PetStoryBlockFactory)
        name = factory.Faker("name")
        date_of_birth = factory.Faker("date_object")
        feeding_schedule = ListBlockFactory(ScheduledFeedingBlockFactory)
        colour = factory.Faker(
            "random_element", elements=[x[0] for x in get_colour_choices()]
        )
        picture = factory.SubFactory(ImageBlockFactory)

        class Meta:
            model = PetBlock

This example illustrates an important point:

- when creating a factory with nested block factories, we must use ``factory.SubFactory`` to refer to those sub-factories lazily; *unless*

- the corresponding sub-block is a ``StreamBlock``, in which case we can use ``StreamFieldFactory`` [1]_ ; *or*

- we're providing a value/factory by other means (e.g. a literal value, a faker instance); *or*

- the corresponding sub-block is a ``ListBlock``.

If the corresponding sub-block is a ``ListBlock``, we use ``ListBlockFactory``, as seen in the declaration for ``feeding_schedule``, above.

The syntax for declaring values for list block elements is similar to that of stream block factories, except:

- there is no shorthand for providing a default value; and

- we do not need to specify the block type, as list block values are homogenous sequences.

The syntax is:

::

    <index>=<value>

Let's create some ``PetBlock`` instances, providing values for the feeding schedule.

.. code:: python

    f.PetBlockFactory()

::

    StructValue([('story', <StreamValue []>),
                 ('name', 'Robert Bradley'),
                 ('date_of_birth', datetime.date(1984, 2, 26)),
                 ('feeding_schedule', <ListValue: []>),
                 ('colour', 'tabby'),
                 ('picture', <Image: An image>)])


Without parameters, an empty ``ListValue`` is generated for ``feeding_schedule``. Let's add some data for a pet that loves tuna.

.. code:: python

    from datetime import time

    f.PetBlockFactory(
        feeding_schedule__0__food="tuna",
        feeding_schedule__0__time=time(6, 0),
        feeding_schedule__1__food="tuna",
        feeding_schedule__1__time=time(12, 0),
        feeding_schedule__2__food="tuna",
        feeding_schedule__2__time=time(18, 0),
    )["feeding_schedule"]

::

    <ListValue: [StructValue([('time', datetime.time(6, 0)), ('portions', 63), ('food', 'tuna')]), StructValue([('time', datetime.time(12, 0)), ('portions', 24), ('food', 'tuna')]), StructValue([('time', datetime.time(18, 0)), ('portions', 38), ('food', 'tuna')])]>


If we only care *when* the pet is fed, we can declare the times only, and the factory mechanisms will take care of the rest.

.. code:: python

    f.PetBlockFactory(
        feeding_schedule__0__time=time(6, 0),
        feeding_schedule__1__time=time(12, 0),
        feeding_schedule__2__time=time(18, 0),
        feeding_schedule__3__time=time(23, 0),
    )["feeding_schedule"]

::

    <ListValue: [StructValue([('time', datetime.time(6, 0)), ('portions', 44), ('food', 'kibble')]), StructValue([('time', datetime.time(12, 0)), ('portions', 29), ('food', 'carrots')]), StructValue([('time', datetime.time(18, 0)), ('portions', 97), ('food', 'tuna')]), StructValue([('time', datetime.time(23, 0)), ('portions', 4), ('food', 'carrots')])]>


As with stream block factories, the aggregated block indices must result in an uninterrupted sequence of integers starting from 0.

Tying it all together
~~~~~~~~~~~~~~~~~~~~~

Let's create our final block factories, and bundle them into the ``PetPageFactory``.

``StreamBlockFactory`` supports sub-classing, just like ``StreamBlock``, so create the following factories in ``home/factories.py``.

.. code:: python

    from home.blocks import CatBlock, DogBlock


    class CatBlockFactory(PetBlockFactory):
        class Meta:
            model = CatBlock


    class DogBlockFactory(PetBlockFactory):
        class Meta:
            model = DogBlock

Then add them to our top-level ``PetsBlockFactory``.

.. code:: python

    from home.blocks import PetsBlock


    class PetsBlockFactory(StreamBlockFactory):
        cat = factory.SubFactory(CatBlockFactory)
        dog = factory.SubFactory(DogBlockFactory)

        class Meta:
            model = PetsBlock

And finally, create ``PetPageFactory``.

.. code:: python

    from wagtail_factories import (
        PageFactory,
        StreamFieldFactory,
    )
    from home.models import PetPage


    class PetPageFactory(PageFactory):
        pets = StreamFieldFactory(PetsBlockFactory)

        class Meta:
            model = PetPage

We've now built a family of factories from the bottom up, that mirrors our data-type definition. The following diagram illustrates the factory hierarchy we've created:

::

    PetPageFactory
    └── pets (StreamFieldFactory)
        └── PetsBlockFactory (StreamBlockFactory)
            ├── cat (SubFactory)
            │   └── CatBlockFactory (PetBlockFactory)
            │       ├── story (StreamFieldFactory)
            │       │   └── PetStoryBlockFactory (StreamBlockFactory)
            │       │       ├── image (SubFactory → ImageBlockFactory)
            │       │       ├── text (Faker)
            │       │       └── link (Faker)
            │       ├── name (Faker)
            │       ├── date_of_birth (Faker)
            │       ├── feeding_schedule (ListBlockFactory)
            │       │   └── ScheduledFeedingBlockFactory (StructBlockFactory)
            │       │       ├── time (Faker)
            │       │       ├── portions (Faker)
            │       │       └── food (Faker)
            │       ├── colour (Faker)
            │       └── picture (SubFactory → ImageBlockFactory)
            └── dog (SubFactory)
                └── DogBlockFactory (PetBlockFactory)
                    [same structure as CatBlockFactory]

This hierarchy shows how each factory builds upon its sub-factories, creating a complete system for generating test data for complex Wagtail stream field structures.

Taking it for a spin
~~~~~~~~~~~~~~~~~~~~

We can now test our factories, and get familiar with the syntax for declaring stream field structures. The simplest use is to call the ``PetPageFactory`` with no parameters.

.. code:: python

    page = f.PetPageFactory()
    page

::

    <PetPage: Test page>


We can see that the stream field is empty.

.. code:: python

    page.pets

::

    <StreamValue []>


Let's create a ``CatBlock`` and a ``DogBlock`` at the top level, using the factory defaults.

.. code:: python

    page = f.PetPageFactory(
        pets__0="cat",
        pets__1="dog",
    )
    page.pets

::

    <StreamValue [<block cat: StructValue([('story', <StreamValue []>), ('name', 'Matthew Armstrong'), ('date_of_birth', datetime.date(2012, 12, 27)), ('feeding_schedule', <ListValue: []>), ('colour', 'tabby'), ('picture', <Image: An image>)])>, <block dog: StructValue([('story', <StreamValue []>), ('name', 'Gregory Nunez'), ('date_of_birth', datetime.date(2016, 10, 5)), ('feeding_schedule', <ListValue: []>), ('colour', 'orange'), ('picture', <Image: An image>)])>]>


The syntax used here mirrors the "default value" syntax described `Using a stream block factory`_, with the added prefix for the stream field name:

::

    pets__0="cat"

    <model field name>__<stream field index>=<block name>

Let's create an instance with some specific values for the ``CatBlock`` struct block.

.. code:: python

    page = f.PetPageFactory(
        pets__0__cat__name="Praxidike",
        pets__0__cat__colour="tabby",
    )
    page.pets[0]

::

    <block cat: StructValue([('story', <StreamValue []>), ('name', 'Praxidike'), ('date_of_birth', datetime.date(1979, 8, 1)), ('feeding_schedule', <ListValue: []>), ('colour', 'tabby'), ('picture', <Image: An image>)])>


The declaration syntax here is:

::

    <field>__<index>__<block name>__<field name>=<value>

What about nested stream blocks? ``CatBlock.story`` is such a block. To declare values, we follow the syntactic patterns we've already encountered for stream values:

::

    <index>=<block name> for a default; or
    <index>__<block name>=<value>

.. code:: python

    page = f.PetPageFactory(
        pets__0__cat__name="Praxidike",
        pets__0__cat__colour="tabby",
        pets__0__cat__story__0="text",
        pets__0__cat__story__1__link="https://http.cat/",
    )
    page.pets[0]

::

    <block cat: StructValue([('story', <StreamValue [<block text: 'Customer religious less beat.'>, <block link: 'https://http.cat/'>]>), ('name', 'Praxidike'), ('date_of_birth', datetime.date(1980, 3, 12)), ('feeding_schedule', <ListValue: []>), ('colour', 'tabby'), ('picture', <Image: An image>)])>


Prax needs to eat, so we should add some entries to the feeding schedule. Recall that the basic syntax for declaring list block elements is:

::

    <index>=<value>

This composes across field and factory boundaries as in our other examples. So, to specify values for the fields of a struct block:

::

    <index>__<field name>=<value>

.. code:: python

    page = f.PetPageFactory(
        pets__0__cat__feeding_schedule__0__time="06:00:00",
        pets__0__cat__feeding_schedule__1__food="tuna",
    )
    page.refresh_from_db()          # Normalizes the time value.
    page.pets[0].value["feeding_schedule"]

::

    <ListValue: [StructValue([('time', datetime.time(6, 0)), ('portions', 37), ('food', 'tuna')]), StructValue([('time', datetime.time(10, 7, 23, 441000)), ('portions', 54), ('food', 'tuna')])]>


Finally, here's an example of specifying multiple fields on multiple stream elements.

.. code:: python

    page = f.PetPageFactory(
        pets__0__cat__name="Frog",
        pets__0__cat__story__0="text",
        pets__0__cat__story__1__link="https://http.cat/",
        pets__1="cat",
        pets__2__dog__name="Werner",
        pets__2__dog__colour="orange",
        pets__2__dog__feeding_schedule__0__time="08:30:00",
        pets__2__dog__feeding_schedule__1__time="12:30:00",
        pets__2__dog__feeding_schedule__2__time="18:30:00",
        pets__2__dog__story__0="text",
        pets__2__dog__picture__image__image__file__width=200,
    )

    page

::

    <PetPage: Test page>


.. [1] Technically we can use ``factory.SubFactory`` instead of ``StreamFieldFactory`` for nested stream block factory declarations, and it is common to see this in the wild. However, this will result in errors if the containing block factory is used directly - i.e. not in the context of a containing model factory with a top level ``StreamFieldFactory``. This discrepancy should be resolved in a future release of wagtail-factories.
