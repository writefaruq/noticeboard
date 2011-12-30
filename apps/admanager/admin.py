from django.contrib import admin

from noticeboard.apps.admanager.models import (Customer, ApprovalManager, AdCategory, Ad,
                PublishRequest, AdStats)


for model in (AdCategory, Ad, PublishRequest, AdStats):
    admin.site.register(model)