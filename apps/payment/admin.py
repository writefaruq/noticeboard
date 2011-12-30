from django.contrib import admin

from noticeboard.apps.payment.models import (AccountBalance, Invoice, InvoicePayment)


for model in (AccountBalance, Invoice, InvoicePayment):
    admin.site.register(model)