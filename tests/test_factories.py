import pytest
from wagtail import blocks
from wagtail.models import Page, Site

import wagtail_factories
from tests.testapp.factories import MyTestPageFactory, MyTestPageGetOrCreateFactory


@pytest.mark.django_db
def test_page_no_args_or_kwargs():
    page = wagtail_factories.PageFactory(parent=None)
    assert page.title == "Test page"
    assert page.slug == "test-page"


@pytest.mark.django_db
def test_page_build_no_args_or_kwargs():
    page = wagtail_factories.PageFactory.build(parent=None)
    assert page.title == "Test page"
    assert page.slug == "test-page"


@pytest.mark.django_db
def test_page_build_no_parent():
    page = wagtail_factories.PageFactory.build()
    assert page.title == "Test page"
    assert page.slug == "test-page"


@pytest.mark.django_db
def test_page_multiple_roots():
    # Make sure the default root pages are removed created by wagtail
    # migrations
    Page.get_root_nodes().delete()
    assert Page.get_root_nodes().count() == 0

    wagtail_factories.PageFactory(parent=None)
    wagtail_factories.PageFactory(parent=None)
    wagtail_factories.PageFactory(parent=None)
    assert Page.get_root_nodes().count() == 3


@pytest.mark.django_db
def test_page_multiple_nested():
    root = wagtail_factories.PageFactory(parent=None)
    page_1 = wagtail_factories.PageFactory(parent=root, slug="page-1")
    wagtail_factories.PageFactory(parent=page_1, slug="page-1-1")
    wagtail_factories.PageFactory(parent=page_1, slug="page-1-2")
    wagtail_factories.PageFactory(parent=page_1, slug="page-1-3")

    page_2 = wagtail_factories.PageFactory(parent=root, slug="page-2")
    wagtail_factories.PageFactory(parent=page_2, slug="page-2-1")
    wagtail_factories.PageFactory(parent=page_2, slug="page-2-2")
    wagtail_factories.PageFactory(parent=page_2, slug="page-2-3")
    wagtail_factories.PageFactory(parent=page_2, slug="page-2-4")

    assert len(root.get_children()) == 2
    assert len(page_1.get_children()) == 3
    assert len(page_2.get_children()) == 4


@pytest.mark.django_db
def test_page_multiple_nested_structure_at_once():
    Page.objects.all().delete()

    page = wagtail_factories.PageFactory(
        slug="page-1-2-3",
        title="Page 1.2.3",
        parent__slug="page-1-2",
        parent__title="Page 1.2",
        parent__parent__slug="page-1",
        parent__parent__title="Page 1",
        parent__parent__parent=None,
    )

    assert Page.objects.count() == 3, Page.objects.all()

    assert page.slug == "page-1-2-3"
    assert page.get_parent().slug == "page-1-2"
    assert page.get_parent().get_parent().slug == "page-1"
    assert page.get_parent().get_parent().get_parent() is None


@pytest.mark.django_db
def test_custom_page_streamfield():
    root_page = wagtail_factories.PageFactory(parent=None)
    page = MyTestPageFactory(parent=root_page)

    assert len(page.body) == 0


@pytest.mark.django_db
def test_custom_page_streamfield_data():
    root_page = wagtail_factories.PageFactory(parent=None)
    values = ["bla-1", "bla-2"]
    page = MyTestPageFactory(
        parent=root_page,
        body=[
            (
                "char_array",
                blocks.list_block.ListValue(
                    blocks.ListBlock(blocks.CharBlock()), values=values
                ),
            )
        ],
    )

    assert page.body[0].block_type == "char_array"
    assert list(page.body[0].value) == values


@pytest.mark.django_db
def test_site_no_args_or_kwargs():
    site = wagtail_factories.SiteFactory()
    assert site.root_page.depth == 1


@pytest.mark.django_db
def test_site_multiple_no_args_or_kwargs():
    Site.objects.all().delete()

    wagtail_factories.SiteFactory()
    wagtail_factories.SiteFactory()
    wagtail_factories.SiteFactory()
    wagtail_factories.SiteFactory()
    assert Site.objects.count() == 4


@pytest.mark.django_db
def test_image_no_args_or_kwargs():
    image = wagtail_factories.ImageFactory()
    assert image.collection.name == "Test collection"


@pytest.mark.django_db
def test_image_add_to_collection():
    root_collection = wagtail_factories.CollectionFactory(parent=None)

    image = wagtail_factories.ImageFactory(
        collection__parent=root_collection, collection__name="new"
    )
    assert image.collection.name == "new"


@pytest.mark.django_db
def test_get_or_create():
    root_page = wagtail_factories.PageFactory(parent=None)
    page_1 = MyTestPageGetOrCreateFactory(
        slug="foobar", parent__slug="root", parent__parent=root_page
    )
    page_2 = MyTestPageGetOrCreateFactory(
        slug="foobar", parent__slug="root", parent__parent=root_page
    )

    assert page_1.pk == page_2.pk


@pytest.mark.django_db
def test_get_or_create_with_root():
    root_page = wagtail_factories.PageFactory(parent=None)
    page_1 = MyTestPageGetOrCreateFactory(slug="foobar", parent=root_page)
    page_2 = MyTestPageGetOrCreateFactory(slug="foobar", parent=root_page)

    assert page_1.pk == page_2.pk


@pytest.mark.django_db
def test_document_add_to_collection():
    root_collection = wagtail_factories.CollectionFactory(parent=None)
    document = wagtail_factories.DocumentFactory(
        collection__parent=root_collection, collection__name="new"
    )
    assert document.collection.name == "new"
