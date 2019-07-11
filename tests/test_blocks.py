from collections import OrderedDict

import pytest
from wagtail.core.blocks import StructValue
from wagtail.images.models import Image

import wagtail_factories
from tests.testapp.factories import MyBlockFactory, MyTestPageWithStreamFieldFactory


@pytest.mark.django_db
def test_list_block_factory():
    value = MyBlockFactory(
        items__0__label='label-1',
        items__0__value=1,
        items__1__label='label-2',
        items__1__value=2,
        image__image=None)

    assert value == StructValue(None, [
        ('title', 'my title'),
        ('item', OrderedDict([
            ('label', 'my-label'),
            ('value', 100),
        ])),
        ('items', [
            StructValue(None, [
                ('label', 'label-1'),
                ('value', 1),
            ]),
            StructValue(None, [
                ('label', 'label-2'),
                ('value', 2),
            ]),
        ]),
        ('image', None),
    ])


@pytest.mark.django_db
def test_block_factory():
    value = MyBlockFactory(
        image__image__title='blub')

    assert value == OrderedDict([
        ('title', 'my title'),
        ('item', OrderedDict([
            ('label', 'my-label'),
            ('value', 100),
        ])),
        ('items', []),
        ('image', Image.objects.first()),
    ])

    assert value['image'].title == 'blub'


def test_block_factory_build():
    value = MyBlockFactory.build(
        image__image__title='blub')

    image = value.pop('image')
    assert image.title == 'blub'

    assert value == OrderedDict([
        ('title', 'my title'),
        ('item', OrderedDict([
            ('label', 'my-label'),
            ('value', 100),
        ])),
        ('items', []),
    ])



@pytest.mark.django_db
def test_block_factory_subkwarg():
    value = MyBlockFactory(
        item__label='my-label',
        item__value=20,
        image__image=None)

    assert value == OrderedDict([
        ('title', 'my title'),
        ('item', OrderedDict([
            ('label', 'my-label'),
            ('value', 20),
        ])),
        ('items', []),
        ('image', None),
    ])


@pytest.mark.django_db
def test_custom_page_streamfield_data_complex():
    assert Image.objects.count() == 0

    root_page = wagtail_factories.PageFactory(parent=None)
    page = MyTestPageWithStreamFieldFactory(
        parent=root_page,
        body__0__char_array__0='foo',
        body__0__char_array__1='bar',
        body__2__int_array__0=100,
        body__1__struct__title='My Title',
        body__1__struct__item__value=100,
        body__1__struct__image__image=None,
        body__3__image__image__title='Blub',
    )
    assert Image.objects.count() == 1
    image = Image.objects.first()

    assert page.body.stream_data == [
        ('char_array', ['foo', 'bar']),
        ('struct', StructValue(None, [
            ('title', 'My Title'),
            ('item', StructValue(None, [
                ('label', 'my-label'),
                ('value', 100),
            ])),
            ('items', []),
            ('image', None),
        ])),
        ('int_array', [100]),
        ('image', image),
    ]
    content = str(page.body)
    assert 'block-image' in content


@pytest.mark.django_db
def test_image_chooser_block():
    value = wagtail_factories.ImageChooserBlockFactory()
    image = Image.objects.last()

    assert value == image
