import pytest

import wagtail_factories
from tests.testapp.factories import MyTestPageFactory
from wagtail.wagtailcore.models import Page, Site


@pytest.mark.django_db
def test_page_no_args_or_kwargs():
    page = wagtail_factories.PageFactory()
    assert page.title == 'Test page'
    assert page.slug == 'test-page'


@pytest.mark.django_db
def test_page_multiple_roots():
    # Make sure the default root pages are removed created by wagtail
    # migrations
    Page.get_root_nodes().delete()
    assert Page.get_root_nodes().count() == 0

    wagtail_factories.PageFactory()
    wagtail_factories.PageFactory()
    wagtail_factories.PageFactory()
    assert Page.get_root_nodes().count() == 3


@pytest.mark.django_db
def test_page_multiple_no_args_or_kwargs():
    root = wagtail_factories.PageFactory()
    page_1 = wagtail_factories.PageFactory(parent=root, slug='page-1')
    wagtail_factories.PageFactory(parent=page_1, slug='page-1-1')
    wagtail_factories.PageFactory(parent=page_1, slug='page-1-2')
    wagtail_factories.PageFactory(parent=page_1, slug='page-1-3')

    page_2 = wagtail_factories.PageFactory(parent=root, slug='page-2')
    wagtail_factories.PageFactory(parent=page_2, slug='page-2-1')
    wagtail_factories.PageFactory(parent=page_2, slug='page-2-2')
    wagtail_factories.PageFactory(parent=page_2, slug='page-2-3')
    wagtail_factories.PageFactory(parent=page_2, slug='page-2-4')

    assert len(root.get_children()) == 2
    assert len(page_1.get_children()) == 3
    assert len(page_2.get_children()) == 4


@pytest.mark.django_db
def test_custom_page_streamfield():
    root_page = wagtail_factories.PageFactory()
    page = MyTestPageFactory(parent=root_page)

    assert page.body.stream_data == []


@pytest.mark.django_db
def test_custom_page_streamfield_data():
    root_page = wagtail_factories.PageFactory()
    page = MyTestPageFactory(
        parent=root_page,
        body=[
            ('char_array', ['bla-1', 'bla-2'])
        ])

    assert page.body.stream_data == [
        ('char_array', ['bla-1', 'bla-2'])
    ]


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
