from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from noticeboard.apps.profiles.models import Profile

from noticeboard.apps.payment.models import AccountBalance, Invoice, InvoicePayment
from noticeboard.apps.payment.forms import PayInvoiceForm
from noticeboard.apps.admanager.models import Customer

@login_required
def payments(request):
    user_profile = Profile.objects.get(user=request.user)
    if user_profile:
        customer = Customer.objects.get(user_profile=user_profile)
    else:
        return render_to_response("homepage.html", context)  ## Replace by 404
    account_balance = AccountBalance.objects.get(customer=customer)
    invoices = Invoice.objects.filter(customer=customer)
    invoice_payments = InvoicePayment.objects.filter(invoice__in=invoices)
    paid_invoices = unpaid_invoices = []
    for ip in invoice_payments:
        paid_invoices.append(ip.invoice)
    unpaid_invoices = list(set(invoices) - set(paid_invoices))
    context = {
        "account_balance": account_balance,
        "paid_invoices": paid_invoices,
        "unpaid_invoices": unpaid_invoices,
    }
    context = RequestContext(request, context)
    return render_to_response("payment/payments.html", context)

def topup(request):
    return payments(request)

def pay_invoice(request, *args, **kwargs):
    template_name = kwargs.pop("template_name", "payment/pay_invoice.html")

    if request.method == "POST" and request.user.is_authenticated():
        user_profile = Profile.objects.get(user=request.user)
        if user_profile:
            customer = Customer.objects.get(user_profile=user_profile)
        else:
            return render_to_response("homepage.html", context)  ## Replace by 404
        account_balance = AccountBalance.objects.get(customer=customer)
        pay_invoice_form = PayInvoiceForm(request.POST)
        if pay_invoice_form.is_valid():
            pay_invoice_form.save(user=request.user)
            ctx = {
                "pay_invoice_form" : pay_invoice_form,
                "account_balance" : account_balance,
            }
        return render_to_response("payment/payments.html", RequestContext(request, ctx))
    else:
        ctx = {
            "pay_invoice_form" : PayInvoiceForm(),
        }

    return render_to_response(template_name, RequestContext(request, ctx))
