======================
Architecture overview
======================

This document provides a high-level overview of wagtail-factories' architecture and design principles.

System components
=================

wagtail-factories extends Factory Boy to create test data for Wagtail CMS models. The system consists of three main layers:

**Factory layer**
    Core factory classes that extend Factory Boy's ``DjangoModelFactory`` for Wagtail-specific models (``PageFactory``, ``ImageFactory``, etc.)

**Block factory layer**
    Specialized factories for Wagtail's block system (``StreamBlockFactory``, ``StructBlockFactory``, ``ListBlockFactory``)

**Builder layer**
    Internal machinery that constructs complex nested structures, particularly for StreamField content. This layer handles the complex challenge of bridging Factory Boy's flat parameter structure with Wagtail's dynamic nested blocks.

Design principles
=================

Factory Boy integration
-----------------------

wagtail-factories is built as an extension to Factory Boy, not a replacement. This means:

- All standard Factory Boy features work (``Sequence``, ``LazyAttribute``, ``SubFactory``, etc.)
- Follows Factory Boy's patterns for extending and customizing behavior
- Leverages Factory Boy's ``StepBuilder`` system for complex object construction

Declaration syntax for nested structures
------------------------------------------

wagtail-factories extends Factory Boy's existing double-underscore syntax for relationships. Where Factory Boy supports::

    UserFactory(profile__bio="Software developer")

wagtail-factories extends this pattern to support indexed, nested StreamField structures::

    MyPageFactory(
        body__0__carousel__items__0__label='Slide 1',
        body__1__text_block__content='Hello world'
    )

This builds on Factory Boy's familiar relationship traversal syntax, adding support for:

- Block indexes (``0``, ``1``) to specify position in StreamField
- Block type selection (``carousel``, ``text_block``)
- Nested field paths within blocks (``items__0__label``)

The key difference is that Factory Boy's relationship syntax refers to static model relationships known at class definition time, while StreamField factories handle dynamic structures only known at runtime.

Wagtail block system mapping
-----------------------------

The factory system mirrors Wagtail's block hierarchy:

.. code-block:: text

    Wagtail Blocks          wagtail-factories
    =============          =================
    StreamBlock       →    StreamBlockFactory
    StructBlock       →    StructBlockFactory
    ListBlock         →    ListBlockFactory
    CharBlock         →    CharBlockFactory
    ImageChooserBlock →    ImageChooserBlockFactory

This 1:1 mapping makes the system intuitive for developers familiar with Wagtail's block system.

Key architectural decisions
===========================

Class-based factory definition
------------------------------

StreamField factories are defined using class-based syntax that mirrors Wagtail's block definitions::

    class MyStreamBlockFactory(StreamBlockFactory):
        text = CharBlockFactory
        image = factory.SubFactory(ImageChooserBlockFactory)
        carousel = factory.SubFactory(CarouselBlockFactory)

        class Meta:
            model = MyStreamBlock

This approach enables nested StreamBlocks, better IDE support, and cleaner factory composition.

.. note::

    A legacy dict-based syntax exists::

        StreamFieldFactory({'text': CharBlockFactory})

    This syntax is deprecated and will be removed in a future version. It does not support nested StreamBlocks.

Factory vs builder separation
------------------------------

**Factories** define the structure and default values:

- Declare available block types
- Set default field values
- Define relationships between blocks

**Builders** handle runtime construction:

- Parse deep object declarations
- Validate parameter structure
- Construct Wagtail block instances
- Handle recursive nesting

This separation allows the factory definitions to remain clean while complex construction logic lives in dedicated builder classes.

Lazy evaluation support
-----------------------

The system preserves Factory Boy's lazy evaluation capabilities even in deeply nested structures::

    class MyStructBlockFactory(StructBlockFactory):
        title = factory.LazyAttribute(lambda obj: f"Title {obj.number}")
        number = factory.Sequence(lambda n: n)

This works correctly even when the StructBlock is nested several levels deep in a StreamField.

Error handling philosophy
=========================

The system provides specific, actionable error messages for common mistakes:

**InvalidDeclaration**
    Malformed parameter syntax or missing required indices

**DuplicateDeclaration**
    Multiple conflicting values for the same stream position

**UnknownChildBlockFactory**
    Reference to undefined block types

This explicit error handling helps developers debug complex factory definitions.

Extensibility
=============

Custom factory classes can be created by extending the provided base classes::

    class CustomStructBlockFactory(StructBlockFactory):
        # Add custom behavior, defaults, etc.

        class Meta:
            model = MyCustomStructBlock

This allows adaptation to domain-specific Wagtail block types while maintaining all the declaration syntax capabilities.

Next steps
==========

**For contributors**: If you need to modify or extend the StreamField factory system, see :doc:`streamfield-internals` for detailed technical implementation details including Factory Boy integration mechanisms, parameter parsing, and builder system architecture.
