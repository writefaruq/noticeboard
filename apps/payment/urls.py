from django.conf.urls.defaults import *
from apps.payment.views import payments, topup, pay_invoice

urlpatterns = patterns("",
    url(r"^$", payments, name="payment_payments"),
    url(r"^topup/$", topup, name="payment_topup"),
    url(r"^pay_invoice/$", pay_invoice, name="payment_pay_invoice"),
)