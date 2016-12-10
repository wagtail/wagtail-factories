from collections import OrderedDict

import pytest

import wagtail_factories
from tests.testapp.factories import MyBlockFactory, MyTestPageWithStreamFieldFactory


@pytest.mark.django_db
def test_list_block_factory():
    value = MyBlockFactory(
        items__0__label='label-1',
        items__0__value=1,
        items__1__label='label-2',
        items__1__value=2)

    assert value == OrderedDict([
        ('title', 'my title'),
        ('item', OrderedDict([
            ('label', 'my-label'),
            ('value', 100),
        ])),
        ('items', [
            OrderedDict([
                ('label', 'label-1'),
                ('value', 1),
            ]),
            OrderedDict([
                ('label', 'label-2'),
                ('value', 2),
            ]),
        ])
    ])


@pytest.mark.django_db
def test_block_factory():
    value = MyBlockFactory()

    assert value == OrderedDict([
        ('title', 'my title'),
        ('item', OrderedDict([
            ('label', 'my-label'),
            ('value', 100),
        ])),
        ('items', [])
    ])


@pytest.mark.django_db
def test_block_factory_subkwarg():
    value = MyBlockFactory(
        item__label='my-label',
        item__value=20)

    assert value == OrderedDict([
        ('title', 'my title'),
        ('item', OrderedDict([
            ('label', 'my-label'),
            ('value', 20),
        ])),
        ('items', [])
    ])


@pytest.mark.django_db
def test_custom_page_streamfield_data_complex():
    root_page = wagtail_factories.PageFactory(parent=None)
    page = MyTestPageWithStreamFieldFactory(
        parent=root_page,
        body__0__char_array__0='foo',
        body__0__char_array__1='bar',
        body__2__int_array__0=100,
        body__1__struct__title='My Title',
        body__1__struct__item__value=100,
    )

    assert page.body.stream_data == [
        ('char_array', ['foo', 'bar']),
        ('struct', OrderedDict([
            ('title', 'My Title'),
            ('item', OrderedDict([
                ('label', 'my-label'),
                ('value', 100),
            ])),
            ('items', [])
        ])),
        ('int_array', [100])
    ]
