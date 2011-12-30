from datetime import datetime, timedelta
from django.db import models

from noticeboard.apps.admanager.models import Customer, PublishRequest, AdStats


### Customer maintains AccountBalace to spend on site services ###

class AccountBalance(models.Model):
    """
    Holds Customers  account balace info
    """
    customer = models.ForeignKey(Customer)
    current_balance = models.DecimalField(max_digits=7, decimal_places=2, default=0, help_text="GBP")
    last_paid_amount = models.DecimalField(max_digits=7, decimal_places=2, default=0, help_text="GBP")
    last_paid_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "%s: %s GBP" %(self.customer, self.current_balance)

    def topup(self, amount):
        self.current_balance += amount
        self.save()

    def deduct(self, amount):
        self.current_balance += amount
        self.save()

### An Invoice is generated when some service is offered/approved to Customer ###

class Invoice(models.Model):
    """
    Payment that would be deducted from AccountBalace
    """
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    created_at = models.DateTimeField(auto_now=True)
    publish_request = models.ForeignKey(PublishRequest)

    def __unicode__(self):
        return "%s: pay %s GBP" %(self.publish_request, self.amount)

    def save(self, *args, **kwargs):
        if not self.id:
            rate = self.publish_request.ad.category.publish_rate
            duration = self.publish_request.publish_day
            self.amount = rate * duration
        super(Invoice, self).save(*args, **kwargs)


### Invoice payment is necessary to render the offered service ###

class InvoicePayment(models.Model):
    """
    As paid by Customer
    """
    invoice = models.ForeignKey(Invoice)
    balace = models.ForeignKey(AccountBalance)
    paid_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "%s paid-at %s" %(self.invoice, self.paid_at)

    def save(self, *args, **kwargs):
        if not self.id: ## side effect of payment
            ad = self.invoice.publish_request.ad
            ad.go_live()
            duration = self.invoice.publish_request.publish_day
            adstats = AdStats.objects.create(
                            ad=ad,
                            expired_at=(datetime.now() + timedelta(days=duration))
                      )
        super(InvoicePayment, self).save(*args, **kwargs)
