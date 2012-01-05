from datetime import datetime
from django import forms
from django.utils.translation import ugettext_lazy as _, ugettext

from noticeboard.apps.profiles.models import Profile
from noticeboard.apps.admanager.models import Customer, PublishRequest
from noticeboard.apps.payment.models import AccountBalance, Invoice, InvoicePayment

class PayInvoiceForm(forms.Form):
    """
    Need to redirect form after save
    """
    category = forms.ModelChoiceField(
        label = _("Invoice"),
        queryset = Invoice.objects.all()
    )
    pay_now = forms.BooleanField(
        label = _("Pay now?"),
    )

    def __init__(self, *args, **kwargs):
        super(PayInvoiceForm, self).__init__(*args, **kwargs)

    def save(self, user):
        """Pays invoice nad makes Ad live"""
        profile = Profile.objects.get(user=user)
        # get the customer, invoice and create an invoice payment
        customer = Customer.objects.filter(user_profile=profile).reverse()[0]
        balance = AccountBalance.objects.filter(customer=customer).reverse()[0]
        # Fix unlink balance with invoice?
        invoice = Invoice.objects.filter(customer=customer).reverse()[0]
        # sent for approval
        if self.cleaned_data['pay_now']:
            balance.deduct(invoice.amount)
            (paid, at) = InvoicePayment.objects.get_or_create(
                        invoice=invoice,
                        balace=balance, ## TODO Fix typo
                         paid_at=datetime.now()
                      )
