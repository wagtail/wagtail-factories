import wagtail_factories

from . import models


class MyTestPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = models.MyTestPage
