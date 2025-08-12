==============================
StreamField internals guide
==============================

This guide provides detailed technical documentation for contributors working on the StreamField block factory system. It covers the internal mechanisms, declaration syntax parsing, builder architecture, and block factory behavior.

.. note::
   This documentation assumes familiarity with Wagtail's block system, Factory Boy basics, and the conceptual overview in :doc:`architecture`.

Factory Boy internals primer
=============================

Before diving into the StreamField system, it's helpful to understand these Factory Boy concepts that are central to the implementation:

**StepBuilder**
    Factory Boy's mechanism for constructing objects step-by-step. When you call ``MyFactory(param="value")``, Factory Boy creates a StepBuilder that processes each parameter and builds the final object. StepBuilder classes can be customized to handle complex construction logic.

**DeclarationSet**
    Factory Boy's internal storage for factory declarations. When you define ``title = "Hello"`` in a factory class, it gets stored in a DeclarationSet. The keys in this set must be valid Python identifiers, which is why wagtail-factories needs key transformation.

**Strategy propagation**
    How Factory Boy passes the build vs create decision through nested factories. When you call ``MyFactory.build()``, all nested ``SubFactory`` calls should also use ``build()``. When you call ``MyFactory.create()``, nested factories should ``create()`` and save to the database.

**Lazy evaluation**
    Factory Boy delays executing ``LazyAttribute`` and ``LazyFunction`` declarations until the object is actually being built. This allows values to depend on other fields or the current build context.

**ParameteredAttribute**
    A Factory Boy mechanism that allows factory attributes to accept parameters. ``StreamFieldFactory`` is a ``ParameteredAttribute`` that accepts block declarations and delegates to appropriate block factories.

The big picture: how it all works together
===========================================

The StreamField factory system translates user declarations into Wagtail block structures. Here's a complete example to illustrate the process:

**Factory definitions**:

.. code-block:: python

    # Define the block structure
    class MyStreamBlockFactory(StreamBlockFactory):
        text_block = factory.SubFactory(CharBlockFactory)
        struct_block = factory.SubFactory(MyStructBlockFactory)
        
        class Meta:
            model = MyStreamBlock
    
    class MyStructBlockFactory(StructBlockFactory):
        title = "Default Title"
        content = "Default Content"
        
        class Meta:
            model = MyStructBlock
    
    # Use in page factory
    class MyPageFactory(factory.Factory):
        body = StreamFieldFactory(MyStreamBlockFactory)
        
        class Meta:
            model = MyPage

**Usage and transformation**:

.. code-block:: text

    Input:  MyPageFactory(body__0__struct_block__title="Hello World")
    Output: MyPage with StreamValue containing StructBlock("Hello World", "Default Content")

This translation happens in three phases:

**Phase 1: Parse the declaration syntax**
    Extract the structure from parameter names like ``body__0__struct_block__title``:

    - StreamField name: ``body`` (matches the ``StreamFieldFactory`` attribute in ``MyPageFactory``)
    - Index: ``0`` (first item in stream)
    - Block type: ``struct_block`` (matches ``MyStreamBlockFactory.struct_block``)
    - Field path: ``title`` (field within ``MyStructBlockFactory``)
    - Value: ``"Hello World"``

**Phase 2: Generate a Factory class dynamically**
    Create a new ``StreamBlockFactory`` subclass that matches the requested structure:

    .. code-block:: python

        # Generated factory equivalent to:
        class DynamicStreamFactory(StreamBlockFactory):
            0.struct_block = factory.SubFactory(StructBlockFactory)

    .. note::
       This is a conceptual illustration. The actual generated class uses attribute names with dots (``0.struct_block``) which aren't valid Python syntax but work through Factory Boy's internal mechanisms.

**Phase 3: Let Factory Boy build the objects**
    Use Factory Boy's normal mechanisms to construct the final ``StreamValue``:

    - The ``SubFactory`` creates the ``StructBlockFactory``
    - Parameters like ``title="Hello"`` get passed to the struct factory
    - Factory Boy handles lazy evaluation, strategy propagation, etc.
    - The final result is a proper Wagtail ``StreamValue`` object

This approach preserves Factory Boy's features while handling the nested structure that Wagtail StreamBlocks require.

Implementation background
==========================

The StreamField factory system is complex because it bridges two incompatible paradigms: Factory Boy's flat parameter structure and Wagtail's dynamic nested blocks.

Factory Boy expects parameters like ``title="Hello"`` that map directly to object attributes. StreamField factories need to handle ``body__0__struct_block__title="Hello"`` - indexed, nested declarations that describe dynamic structures unknown until runtime.

Early implementations bypassed Factory Boy entirely but lost features like lazy evaluation and build/create strategies. The current approach generates Factory classes dynamically based on user parameters, preserving Factory Boy integration while handling the structural complexity.

Declaration syntax and parsing
===============================

The StreamField factory system supports a sophisticated declaration syntax that allows deep nesting and precise control over block construction. Understanding how this syntax is parsed is crucial for maintaining and extending the system.

Core syntax patterns
---------------------

The system recognizes two primary declaration patterns:

**Parametric declarations**::

    body__0__struct_block__title="Hello World"

This creates a ``struct_block`` at index 0 with its ``title`` field set to "Hello World".

**Block type declarations**::

    body__0="struct_block"

This creates a ``struct_block`` at index 0 using factory defaults.

Deep declaration parsing
-------------------------

Declaration parsing occurs in ``StreamBlockStepBuilder.get_block_declarations()``:

.. code-block:: python

    def get_block_declarations(self, factory_meta, extras):
        indexed_block_names = {}  # Maps index -> block_name
        extra_declarations = {}   # Maps transformed keys -> values

        for k, v in extras.items():
            if k.isdigit():
                # Handle: body__0="struct_block"
                indexed_block_names[int(k)] = v
            else:
                # Handle: body__0__struct_block__title="foo"
                i, name, *params = k.split("__", maxsplit=2)
                indexed_block_names[int(i)] = name
                transformed_key = self.reconstruct_key(i, name, params)
                extra_declarations[transformed_key] = v

Key transformation process
--------------------------

Parameters like ``body__0__struct_block__title="foo"`` undergo this transformation:

1. **Split**: ``["0", "struct_block", "title"]``
2. **Extract**: index=0, name="struct_block", params=["title"]
3. **Transform**: ``"0.struct_block__title"`` (note the dot separator)
4. **Store**: ``extra_declarations["0.struct_block__title"] = "foo"``

The dot-separated format (``0.struct_block__title``) is crucial because:

- It creates unique, hashable keys for Factory Boy's DeclarationSet
- The dot prevents Factory Boy from treating "0" as an unknown declaration
- It maintains hierarchical structure needed for nested construction

Complex declaration examples
-----------------------------

**Deep nesting**::

    body__0__struct_block__inner_stream__1__char_block="text"

Represents:
- StreamField ``body``
- Index 0: StructBlock ``struct_block``
- Field ``inner_stream``: Nested StreamBlock
- Index 1: CharBlock with value "text"

**ListBlock with StreamBlock items**::

    body__0__list_block__0__0__struct_block__title="foo"

Parameter breakdown:
- First ``0``: StreamField index
- ``list_block``: Block name
- Second ``0``: ListBlock item index
- Third ``0``: Inner StreamBlock index
- ``struct_block__title``: Nested structure

Builder system architecture
============================

The builder system is the core machinery that transforms parsed declarations into Wagtail block structures.

.. important::
   **Why custom builders?**

   Factory Boy's built-in StepBuilder assumes static factory declarations known at class definition time. StreamField factories need to handle dynamic structures where the required blocks and their indexes are only known when the factory is called.

   Custom builders solve this by:

   - Parsing indexed parameter syntax that Factory Boy doesn't understand
   - Dynamically generating factory classes based on user parameters
   - Preserving Factory Boy features like lazy evaluation and strategy propagation

StreamBlockStepBuilder construction flow
----------------------------------------

**1. Initialization phase**:

.. code-block:: python

    def __init__(self, factory_meta, extras, strategy):
        indexed_block_names, extra_declarations = self.get_block_declarations(factory_meta, extras)
        new_factory_class = self.create_factory_class(factory_meta, indexed_block_names)
        super().__init__(new_factory_class._meta, extra_declarations, strategy)

**2. Dynamic factory generation**:

- Creates a new ``StreamBlockFactory`` subclass at runtime
- Adds declarations for each requested block: ``{f"{index}.{name}": declared_value}``
- Example: ``{"0.struct_block": SubFactory(StructBlockFactory)}``

**3. Recursive construction**:

- Factory Boy handles the actual object construction
- Each sub-factory gets its own builder with filtered parameters
- Deep nesting is supported through recursive ``SubFactory`` calls

.. important::
   **Multiple builder instances in complex nesting**
   
   When StreamBlocks contain other StreamBlocks (either directly or through ListBlocks), the system creates multiple ``StreamBlockStepBuilder`` instances:
   
   - Each level of StreamBlock nesting gets its own builder instance
   - ListBlocks containing StreamBlocks trigger additional builder creation
   - Each builder processes one level of the parameter hierarchy
   - This recursive pattern scales to arbitrary nesting depths

Block definition propagation
-----------------------------

A sophisticated system ensures nested StreamBlocks have proper block definitions:

.. code-block:: python

    if block_def is not None and isinstance(declared_value, SubFactory):
        child_def = block_def.child_blocks[name]
        if isinstance(child_def, blocks.ListBlock):
            child_def = child_def.child_block  # Special handling for ListBlock
        declared_value.get_factory()._meta.block_def = child_def

This allows anonymous StreamBlocks (declared inline) to construct proper ``StreamValue`` objects.

Parameter flow and delegation
=============================

The builder system creates the factory structure, but how do parameters actually flow through this structure at runtime? This section explains the delegation mechanism that connects user input to the final constructed objects.

Understanding how parameters flow through the recursive builder system is essential for debugging and extending functionality. The key insight is that each level strips its own prefix and delegates remaining parameters to child builders.

Parameter stripping and delegation process
------------------------------------------

Each ``ParameteredAttribute`` (like ``StreamFieldFactory``) receives parameters and:

1. **Filters its own parameters** by prefix matching
2. **Strips its prefix** from matching parameters  
3. **Delegates stripped parameters** to its target factory

**Example: ``body__0__struct_block__title="Hello"``**

.. code-block:: text

    Level 1: MyPageFactory
    ├── Receives: body__0__struct_block__title="Hello"
    ├── StreamFieldFactory "body" matches prefix
    ├── Strips "body__" → delegates: 0__struct_block__title="Hello"
    
    Level 2: StreamBlockFactory  
    ├── Receives: 0__struct_block__title="Hello"
    ├── Builder parses: index=0, block="struct_block", params=["title"]
    ├── Creates SubFactory for StructBlockFactory
    ├── Delegates: title="Hello"
    
    Level 3: StructBlockFactory
    ├── Receives: title="Hello"
    ├── Sets struct field directly
    └── Returns: StructValue with title="Hello"

Why the stripping happens
-------------------------

.. important::
   **Parameter namespace isolation**
   
   Each factory level needs to process only its relevant parameters. Without prefix stripping:
   
   - ``StreamBlockFactory`` would receive ``body__0__title`` - but "body" is meaningless at the block level
   - ``StructBlockFactory`` would receive ``body__0__struct_block__title`` - all the prefixes are irrelevant
   
   Stripping creates clean parameter namespaces: ``title="Hello"`` is exactly what ``StructBlockFactory`` expects.

Recursive delegation examples
-----------------------------

**Simple nesting**: ``body__0__struct_block__title="Hello"``

.. code-block:: text

    MyPageFactory(body__0__struct_block__title="Hello")
    │
    ├─ StreamFieldFactory.evaluate()
    │  └─ receives: {"body__0__struct_block__title": "Hello"}
    │  └─ filters for "body__" prefix
    │  └─ delegates: {"0__struct_block__title": "Hello"}
    │
    ├─ StreamBlockFactory via StreamBlockStepBuilder  
    │  └─ receives: {"0__struct_block__title": "Hello"}
    │  └─ parses: index=0, block="struct_block", field="title"
    │  └─ creates: SubFactory(StructBlockFactory, title="Hello")
    │
    └─ StructBlockFactory
       └─ receives: {"title": "Hello"}
       └─ creates: StructValue(title="Hello")

**Deep nesting**: ``body__0__struct__inner_stream__1__char_block="text"``

.. code-block:: text

    MyPageFactory(body__0__struct__inner_stream__1__char_block="text")
    │
    ├─ StreamFieldFactory "body"
    │  └─ strips "body__" → delegates: "0__struct__inner_stream__1__char_block"
    │
    ├─ StreamBlockStepBuilder (level 1)
    │  └─ parses: index=0, block="struct", remaining="inner_stream__1__char_block"
    │  └─ creates: SubFactory(StructBlockFactory, inner_stream__1__char_block="text")
    │
    ├─ StructBlockFactory  
    │  └─ receives: {"inner_stream__1__char_block": "text"}
    │  └─ has inner_stream = StreamFieldFactory(...)
    │  └─ delegates: {"1__char_block": "text"}
    │
    ├─ StreamBlockStepBuilder (level 2)
    │  └─ parses: index=1, block="char_block", remaining=""
    │  └─ creates: SubFactory(CharBlockFactory, value="text") 
    │
    └─ CharBlockFactory
       └─ receives: {"value": "text"} (or direct assignment)
       └─ creates: CharBlock with value "text"

**ListBlock with nested StreamBlock**: ``body__0__list_block__0__0__struct_block__title="foo"``

Based on verified execution tracing, this complex flow involves multiple builder instances:

.. code-block:: text

    Level 1: StreamFieldFactory.evaluate()
    └─ receives: {'0__list_block__0__0__struct_block__title': 'foo'}
    
    Level 2: StreamBlockStepBuilder (outer)
    └─ parses: index=0, block='list_block'
    └─ delegates: {'0__0__struct_block__title': 'foo'} to ListBlockFactory
    
    Level 3: ListBlockFactory.evaluate()  
    └─ groups by list index: result[0] = {'0__struct_block__title': 'foo'}
    └─ calls step.recurse() → creates child StreamBlockFactory
    
    Level 4: StreamBlockStepBuilder (inner)
    └─ receives: {'0__struct_block__title': 'foo'}
    └─ parses: index=0, block='struct_block'
    └─ creates: StructBlockFactory with title='foo'

.. note::
   The actual parameter flow is more complex than initially documented. ListBlocks containing StreamBlocks create **two separate** ``StreamBlockStepBuilder`` instances, not just nested factory calls.

Implementation details
----------------------

**StreamFieldFactory parameter delegation**:

.. code-block:: python

    def evaluate(self, instance, step, extra):
        # The 'extra' parameter already contains parameters filtered by Factory Boy
        # for this StreamFieldFactory (e.g., all parameters starting with "body__")
        # with the "body__" prefix already stripped by Factory Boy's mechanisms
        return self.stream_block_factory(**extra)

.. important::
   **Factory Boy handles prefix stripping automatically**
   
   The ``ParameteredAttribute`` mechanism performs prefix filtering **before** our code runs:
   
   1. **User calls**: ``MyPageFactory(body__0__struct_block__title="foo")``
   2. **Factory Boy processes**: Identifies ``body__`` prefix matches ``StreamFieldFactory`` 
   3. **Factory Boy strips**: Removes ``body__`` prefix from matching parameters
   4. **Our code receives**: ``StreamFieldFactory.evaluate()`` gets ``{'0__struct_block__title': 'foo'}``
   
   This timing is crucial - our parameter parsing code never sees the original full parameter names.

**Builder parameter parsing**:

.. code-block:: python

    def get_block_declarations(self, factory_meta, extras):
        # At this level, prefixes are already stripped
        # "0__struct_block__title" becomes index=0, block="struct_block", params=["title"]
        for k, v in extras.items():
            if not k.isdigit():
                i, name, *params = k.split("__", maxsplit=2)
                # params becomes ["title"] for nested delegation
                if params:
                    nested_key = "__".join(params)  # "title"
                    # This gets passed to the SubFactory

Critical flow points
--------------------

1. **Entry point filtering**: Each ``StreamFieldFactory`` only processes its own parameters
2. **Prefix stripping**: Essential for clean delegation to child factories
3. **Recursive parsing**: Each builder level handles one level of nesting
4. **Parameter transformation**: Keys get transformed for Factory Boy compatibility (``0.struct_block__title``)
5. **Factory Boy delegation**: Standard ``SubFactory`` mechanisms handle the final construction

Complex flow example
---------------------

For ``body__0__struct__inner_stream__1__char_block="text"``:

1. First-level parsing creates ``struct`` at index 0
2. ``inner_stream__1__char_block="text"`` passed to StructBlockFactory
3. StructBlockFactory creates inner StreamFieldFactory for ``inner_stream``
4. Inner factory parses ``1__char_block="text"``
5. Recursive construction builds the full hierarchy

.. note::
   **Verification**: The parameter flows documented in this section have been verified through live debugging of actual factory execution. See :doc:`parameter-flow-investigation` for detailed tracing results that confirm these documented behaviors.

Block factory behavior
=======================

Each block factory type has specific behavior patterns and construction logic.

StreamBlockFactory
-------------------

**Primary role**: Constructs StreamValue objects from indexed block declarations

**Key methods**:

- ``_construct_stream()``: Creates the final StreamValue from parsed data
- ``_generate()``: Orchestrates the building process via StreamBlockStepBuilder

**Stream construction logic**:

.. code-block:: python

    def _construct_stream(cls, block_class, *args, **kwargs):
        # Parse indexed declarations like "0.struct_block": value
        stream_length = max(map(get_index, kwargs.keys())) + 1 if kwargs else 0
        stream_data = [None] * stream_length
        for indexed_block_name, value in kwargs.items():
            i, name = indexed_block_name.split(".")
            stream_data[int(i)] = (name, value)

        # Convert to StreamValue if block definition available
        block_def = cls._meta.get_block_definition()
        if block_def is None:
            return stream_data  # Legacy format
        return blocks.StreamValue(block_def, stream_data)

StructBlockFactory
------------------

**Primary role**: Creates StructValue objects with named field access

**Construction process**:

.. code-block:: python

    def _construct_struct_value(cls, block_class, params):
        return block_class._meta_class.value_class(
            block_class(),
            list(params.items()),
        )

**Declaration patterns**:

- ``title="Hello"`` - Direct field assignment
- ``nested_struct__field="value"`` - Nested structure access

ListBlockFactory
-----------------

**Primary role**: Constructs ListBlock values with indexed item access

**Declaration syntax**:

- ``items__0__label="foo"`` - Set field in first StructBlock item
- ``char_array__0="hello"`` - Set first item in CharBlock list  
- ``list_block__0__0__struct_block__title="foo"`` - ListBlock containing StreamBlocks

.. note::
   ListBlock items use consecutive integers only - no block names for list items. When ListBlocks contain StreamBlocks, inner blocks do have names.

**Implementation**:

.. code-block:: python

    def evaluate(self, instance, step, extra):
        result = defaultdict(dict)
        for key, value in extra.items():
            if key.isdigit():
                result[int(key)]["value"] = value
            else:
                prefix, label = key.split("__", maxsplit=1)
                if prefix and prefix.isdigit():
                    result[int(prefix)][label] = value

        subfactory = self.get_factory()
        force_sequence = step.sequence if self.FORCE_SEQUENCE else None
        values = [
            step.recurse(subfactory, params, force_sequence=force_sequence)
            for _, params in sorted(result.items())
        ]

        list_block_def = blocks.list_block.ListBlock(subfactory._meta.model())
        return blocks.list_block.ListValue(list_block_def, values)

**Complex case: StreamBlocks in ListBlocks**

For ``body__0__list_block__0__0__struct_block__title="foo"``:

.. code-block:: text

    Level 1: StreamFieldFactory.evaluate()  
    └─ receives: {'0__list_block__0__0__struct_block__title': 'foo'}
    └─ (Factory Boy already stripped 'body__' prefix)

    Level 2: First StreamBlockStepBuilder.get_block_declarations()
    └─ receives: {'0__list_block__0__0__struct_block__title': 'foo'}  
    └─ parses: index=0, block='list_block'
    └─ delegates: {'0__0__struct_block__title': 'foo'} to ListBlockFactory

    Level 3: ListBlockFactory.evaluate()
    └─ groups by list index: result[0] = {'0__struct_block__title': 'foo'}
    └─ delegates to child StreamBlockFactory: {'0__struct_block__title': 'foo'}

    Level 4: Second StreamBlockStepBuilder.get_block_declarations()  
    └─ receives: {'0__struct_block__title': 'foo'}
    └─ parses: index=0, block='struct_block' 
    └─ creates: SubFactory(StructBlockFactory, title='foo')

    Level 5: StructBlockFactory._build()
    └─ receives: {'title': 'foo'}
    └─ creates: StructValue with title='foo'

Result: ``page.body[0].value[0][0].value["title"] == "foo"``

.. note::
   **Multiple builder instances**: Complex nesting creates multiple ``StreamBlockStepBuilder`` instances. The first handles the outer StreamBlock, the second handles the nested StreamBlock within the ListBlock. This recursive pattern continues for deeper nesting levels.

StreamFieldFactory (ParameteredAttribute)
------------------------------------------

**Primary role**: Entry point that bridges Factory Boy declarations to StreamBlock construction

**Key features**:

- Supports both dict-based and class-based StreamBlock factory definitions
- Delegates to a ``StreamBlockFactory`` subclass for actual construction
- **Automatic block definition setup**: When initialized with a class-based factory, automatically instantiates the model to provide block definitions

**Initialization patterns**:

.. code-block:: python

    # Dict-based (deprecated)
    body = StreamFieldFactory({
        "block_name": BlockFactory,
    })

    # Class-based (recommended)  
    body = StreamFieldFactory(MyStreamBlockFactory)

**Block definition instantiation**:

When using class-based factories, ``StreamFieldFactory.__init__`` automatically sets up block definitions:

.. code-block:: python

    def __init__(self, block_types, **kwargs):
        # ... validation logic ...
        elif isinstance(block_types, type) and issubclass(block_types, StreamBlockFactory):
            # Automatic block definition instantiation
            block_types._meta.block_def = block_types._meta.model()
            self.stream_block_factory = block_types

This automatic instantiation ensures that:

- Block definitions are available for proper ``StreamValue`` construction
- Nested ``SubFactory`` calls receive the correct child block definitions
- The factory system can validate block names and structure at runtime

Factory configuration system
=============================

The options system provides a configuration layer for factory behavior, extending Factory Boy's standard options with Wagtail-specific features.

BlockFactoryOptions
-------------------

**File**: ``src/wagtail_factories/options.py`` (lines 5-28)

Base options class for all block factories:

.. code-block:: python

    class BlockFactoryOptions(FactoryOptions):
        def _build_default_options(self):
            options = super()._build_default_options()
            options.append(OptionDefault("block_def", None))
            return options

**Key features**:

- **``block_def`` option**: Stores the Wagtail block definition for proper ``StreamValue`` construction
- **``get_block_definition()``**: Provides access to block definitions, either from ``block_def`` or by instantiating the ``model``

StreamBlockFactoryOptions
-------------------------

**File**: ``src/wagtail_factories/options.py`` (lines 30-61)

Specialized options for StreamBlock factories with advanced parameter filtering:

.. code-block:: python

    class StreamBlockFactoryOptions(BlockFactoryOptions):
        def prepare_arguments(self, attributes):
            def get_block_name(key):
                # Keys at this point will be like <index>.<block_name>
                return key.split(".")[1]

            kwargs = dict(attributes)
            kwargs = self.factory._adjust_kwargs(**kwargs)

            # Filter out excluded, parameter, and SKIP declarations
            filtered_kwargs = {}
            for k, v in kwargs.items():
                block_name = get_block_name(k)
                if (
                    block_name not in self.exclude
                    and block_name not in self.parameters  
                    and v is not declarations.SKIP
                ):
                    filtered_kwargs[k] = v

            return (), filtered_kwargs

**Key features**:

- **Parameter filtering**: Removes excluded and skipped block declarations
- **Block name extraction**: Parses ``index.block_name`` format to identify which blocks are being used
- **Factory adjustment hooks**: Supports custom parameter processing through ``_adjust_kwargs``

Block definition management
---------------------------

The options system manages how block definitions are passed through the factory hierarchy:

.. code-block:: python

    def get_block_definition(self):
        if self.block_def is not None:
            return self.block_def  # Explicitly set
        elif self.model is not None:
            return self.model()    # Auto-instantiate from model

This enables two patterns:

**Explicit block definition**:

.. code-block:: python

    class MyStreamBlockFactory(StreamBlockFactory):
        class Meta:
            model = MyStreamBlock
            block_def = MyStreamBlock()  # Explicit

**Auto-instantiation** (more common):

.. code-block:: python

    class MyStreamBlockFactory(StreamBlockFactory):  
        class Meta:
            model = MyStreamBlock  # Auto-instantiated when needed

.. important::
   **Why block definitions matter**
   
   Wagtail block definitions are required to construct proper ``StreamValue`` objects. Without them, the system falls back to returning raw data structures. The options system ensures block definitions are available throughout the factory hierarchy by:
   
   - Auto-instantiating models when needed
   - Propagating definitions through ``SubFactory`` chains  
   - Providing consistent access via ``get_block_definition()``

Error handling and validation
==============================

The system provides comprehensive error handling with specific exception types and validation rules.

.. important::
   **Why extensive validation?**

   StreamField factories have complex requirements that Factory Boy doesn't naturally enforce:

   - **Sequential indexes**: Wagtail StreamBlocks require indexes 0, 1, 2... without gaps
   - **Consistent block names**: The same index can't refer to different block types
   - **Valid block references**: All referenced block factories must be defined

   Without upfront validation, users get confusing errors deep in the Wagtail/Factory Boy stack. Custom validation provides clear error messages that point directly to the problem.

Validation rules
----------------

**Sequential index validation**:

.. code-block:: python

    def validate_block_indexes_sequential(self, indexed_block_names, factory_meta):
        indexes = sorted(indexed_block_names.keys())
        for declared, expected in zip_longest(indexes, range(max(indexes) + 1)):
            if declared != expected:
                raise InvalidDeclaration(f"missing required index {expected}")

**Duplicate detection**:

.. code-block:: python

    if key in indexed_block_names and indexed_block_names[key] != name:
        raise DuplicateDeclaration(
            f"Multiple declarations for index {key} (got {name}, already have {indexed_block_names[key]})"
        )

**Block type validation**:

.. code-block:: python

    if v not in factory_meta.base_declarations:
        raise UnknownChildBlockFactory(f"No factory defined for block '{v}'")

Extending the system
=====================

Adding support for new block types
-----------------------------------

To add support for a new Wagtail block type, follow this pattern:

**1. Create a factory class extending the appropriate base**:

.. code-block:: python

    class MyCustomBlockFactory(StructBlockFactory):
        # Define default field values
        title = "Default Title"
        content = factory.LazyAttribute(lambda obj: f"Generated content {obj.id}")

        class Meta:
            model = MyCustomBlock

**2. For blocks requiring custom construction logic**:

.. code-block:: python

    class ComplexBlockFactory(factory.Factory):
        class Meta:
            model = ComplexBlock

        @classmethod
        def _create(cls, model_class, **kwargs):
            # Custom construction logic here
            return model_class(**processed_kwargs)

**3. For blocks that need special StepBuilder handling**:

.. code-block:: python

    class CustomBlockStepBuilder(BaseBlockStepBuilder):
        def evaluate(self, instance, step, extra):
            # Custom parameter processing
            processed_params = self.process_custom_syntax(extra)
            return super().evaluate(instance, step, processed_params)

    class CustomBlockFactory(factory.Factory):
        _BUILDER_CLASS = CustomBlockStepBuilder

        class Meta:
            model = CustomBlock

Integration patterns
--------------------

**Adding to existing StreamBlock factories**:

.. code-block:: python

    class MyStreamBlockFactory(StreamBlockFactory):
        text = factory.SubFactory(CharBlockFactory)
        image = factory.SubFactory(ImageChooserBlockFactory)
        custom = factory.SubFactory(MyCustomBlockFactory)  # Add your custom block

        class Meta:
            model = MyStreamBlock

**Testing new block factories**:

.. code-block:: python

    def test_custom_block_factory():
        # Test basic construction
        block_value = MyCustomBlockFactory()
        assert isinstance(block_value, MyCustomBlock)

        # Test parameter handling
        block_value = MyCustomBlockFactory(title="Test Title")
        assert block_value['title'] == "Test Title"

        # Test in StreamField context
        page = MyPageFactory(body__0="custom", body__0__custom__title="Stream Title")
        assert page.body[0].value['title'] == "Stream Title"

Glossary
=========

**Block definition propagation**
    The process of passing Wagtail block definitions through nested factory calls so that anonymous StreamBlocks can construct proper ``StreamValue`` objects.

**Deep object declaration**
    The syntax that allows specifying nested structure parameters like ``body__0__struct_block__title="Hello"`` in a single factory call.

**Dynamic factory generation**
    The core technique where ``StreamBlockStepBuilder`` creates new factory classes at runtime based on user-requested block combinations.

**Key transformation**
    Converting parameter names like ``body__0__struct_block__title`` into Factory Boy-compatible keys like ``0.struct_block__title``.

**Sequential index validation**
    Ensuring that StreamField indexes are consecutive starting from 0, since Wagtail requires this structure.

**Strategy propagation**
    Factory Boy's mechanism for ensuring that build/create decisions flow correctly through nested ``SubFactory`` calls.
