from django.contrib import admin

from noticeboard.apps.admanager.models import (Customer, ApprovalManager, AdCategory, Ad,
                PublishRequest,PublishApproval, PublishFeePayment, AdStats)


for model in (AdCategory, Ad, PublishRequest, PublishApproval,
            PublishFeePayment, AdStats):
    admin.site.register(model)