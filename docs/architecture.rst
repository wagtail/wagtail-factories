======================
Architecture Overview
======================

This document provides a high-level overview of wagtail-factories' architecture and design principles.

System Components
=================

wagtail-factories extends Factory Boy to create test data for Wagtail CMS models. The system consists of three main layers:

**Factory Layer**
    Core factory classes that extend Factory Boy's ``DjangoModelFactory`` for Wagtail-specific models (``PageFactory``, ``ImageFactory``, etc.)

**Block Factory Layer** 
    Specialized factories for Wagtail's block system (``StreamBlockFactory``, ``StructBlockFactory``, ``ListBlockFactory``)

**Builder Layer**
    Internal machinery that constructs complex nested structures, particularly for StreamField content

Design Principles
=================

Factory Boy Integration
-----------------------

wagtail-factories is built as an extension to Factory Boy, not a replacement. This means:

- All standard Factory Boy features work (``Sequence``, ``LazyAttribute``, ``SubFactory``, etc.)
- Follows Factory Boy's patterns for extending and customizing behavior
- Leverages Factory Boy's ``StepBuilder`` system for complex object construction

Deep Object Declaration
-----------------------

The signature feature is support for "deep object declaration" syntax::

    MyPageFactory(
        body__0__carousel__items__0__label='Slide 1',
        body__1__text_block__content='Hello world'
    )

This allows declarative construction of deeply nested StreamField content without requiring pre-built factory instances.

Wagtail Block System Mapping
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

Key Architectural Decisions
===========================

Class-Based Factory Definition
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

Factory vs Builder Separation
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

Lazy Evaluation Support
-----------------------

The system preserves Factory Boy's lazy evaluation capabilities even in deeply nested structures::

    class MyStructBlockFactory(StructBlockFactory):
        title = factory.LazyAttribute(lambda obj: f"Title {obj.number}")
        number = factory.Sequence(lambda n: n)

This works correctly even when the StructBlock is nested several levels deep in a StreamField.

Error Handling Philosophy
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

This allows adaptation to domain-specific Wagtail block types while maintaining all the deep object declaration capabilities.