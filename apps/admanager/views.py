from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

from apps.admanager.models import Ad
from apps.admanager.forms import CreateAdForm


@login_required
def ads(request):
    """
    Lists ads of current user
    """
    ads = Ad.objects.filter(owner=request.user)
    context = {
        "ads": ads,
    }
    context = RequestContext(request, context)
    return render_to_response("admanager/ads.html", context)

@login_required
def create_ad(request, *args, **kwargs):
    template_name = kwargs.pop("template_name", "admanager/create_ad.html")

    if request.method == "POST" and request.user.is_authenticated():
        ads = Ad.objects.filter(owner=request.user)
        create_ad_form = CreateAdForm(request.POST)
        if create_ad_form.is_valid():
            create_ad_form.save(user=request.user)
            ctx = {
                "create_ad_form": create_ad_form,
                "ads": ads,
            }
        return render_to_response("admanager/ads.html", RequestContext(request, ctx))
    else:
        ctx = {
            "create_ad_form": CreateAdForm(),
        }

    return render_to_response(template_name, RequestContext(request, ctx))

def ad_stats(request):
    return ads(request)

