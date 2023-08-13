# wagtail-factories

Factory boy classes for Wagtail CMS

- [Status](#status)
- [Installation](#installation)
- [Usage](#usage)
  * [Using StreamBlockFactory](#using-streamblockfactory)
  * [Alternative StreamFieldFactory declaration syntax](#alternative-streamfieldfactory-declaration-syntax)
  * [Providing default values for StreamBlock and StreamField factories](#providing-default-values-for-streamblock-and-streamfield-factories)
- [Developing wagtail-factories](#developing-wagtail-factories)
  * [Testing](#running-the-tests)
  * [Formatting](#formatting)

## Status

[![image](https://readthedocs.org/projects/wagtail-factories/badge/?version=latest)](https://readthedocs.org/projects/wagtail-factories/)
[![image](https://github.com/wagtail/wagtail-factories/workflows/Python%20Tests/badge.svg)](https://github.com/wagtail/wagtail-factories/actions?query=workflow%3A%22Python+Tests%22)
[![image](https://img.shields.io/pypi/v/wagtail-factories.svg)](https://pypi.python.org/pypi/wagtail-factories/)

## Installation

``` shell
pip install wagtail-factories
```

## Usage

Documentation is still in progress, but see the
[tests](https://github.com/wagtail/wagtail-factories/tree/main/tests)
for more examples.

``` python
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
```

### Using StreamBlockFactory

`StreamBlockFactory` can be used in conjunction with the other block
factory types to create complex, nested `StreamValues`, much like how
`StreamBlock` can be used to declare the blocks for a complex
`StreamField`.

First, define your `StreamBlockFactory` subclass, using
`factory.SubFactory` to wrap child block declarations. Be sure to
include your `StreamBlock` subclass as the model attribute on the inner
`Meta` class.

``` python
class MyStreamBlockFactory(wagtail_factories.StreamBlockFactory):
    my_struct_block = factory.SubFactory(MyStructBlockFactory)

    class Meta:
        model = MyStreamBlock
```

Then include your `StreamBlockFactory` subclass on a model factory as
the argument to a `StreamFieldFactory`.

``` python
class MyPageFactory(wagtail_factories.PageFactory):
    body = wagtail_factories.StreamFieldFactory(MyStreamBlockFactory)

    class Meta:
        model = MyPage
```

You can then use a modified version of factory\_boy\'s deep object
declaration syntax to build up `StreamValues` on the fly.

``` python
MyPageFactory(
    body__0__my_struct_block__some_field="some value",
    body__0__my_struct_block__some_other_field="some other value",
)
```

To generate the default value for a block factory, terminate your
declaration at the index and provide the block name as the value.

``` python
MyPageFactory(body__0="my_struct_block")
```

### Alternative StreamFieldFactory declaration syntax

Prior to version 3.0, `StreamFieldFactory` could only be used by
providing a dict mapping block names to block factory classes as the
single argument, for example:

``` python
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
```

This style of declaration is still supported, with the caveat that
nested stream blocks are not supported for this approach. From version
3.0, all `BlockFactory` values in a `StreamFieldFactory` definition of
this style *must* be wrapped in factory\_boy `SubFactories`. For
example, the above example must be updated to the following for 3.0
compatibility.

``` python
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
```

This requirement does *not* apply to `ListBlockFactory`, which is a
subclass of `SubFactory`.

### Providing default values for StreamBlock and StreamField factories

Default values for stream fields can be provided in two ways. The
first way is to provide per-stream-block-factory defaults, on a given
`StreamBlockFactory`'s `Meta` class:

``` python
class MyStreamBlockFactory(wagtail_factories.StreamBlockFactory):
    text = wagtail_factories.CharBlockFactory()

    class Meta:
        default_block_values = {
            "0__text": "some default text"
        }
```

In this example, every `StreamValue` created by `MyStreamBlockFactory`
will have the text "some default text" as the value of its first
element, unless it is overridden elsewhere.

Default values can also be provided as an argument to
`StreamFieldFactory`, as shown in the following example:

``` python
class MyPageFactory(wagtail_factories.PageFactory):
    body = wagtail_factories.StreamFieldFactory(
        MyStreamBlockFactory,
        default_block_values={
            "0__text": "some default text"
        },
    )
```

The following precedence is given to values provided for stream field
factories, highest precedence first:

1. values provided by the parent factory, e.g. via parameters to a
   `PageFactory` instantiation;
2. `default_block_values` passed as a parameter to a
   `StreamFieldFactory` instantiation; and
3. `default_block_values` declared on a `StreamBlockFactory`
   subclass's `Meta` class.

## Developing wagtail-factories

Install the dev requirements:

``` shell
pip install -e .[docs,test]
```

### Running the tests

``` shell
DJANGO_SETTINGS_MODULE=tests.settings pytest
```

### Formatting

Format code with `black`:

``` shell
black src tests
```

Perform linting and additional formatting with `ruff`:

``` shell
ruff check . --fix
```
