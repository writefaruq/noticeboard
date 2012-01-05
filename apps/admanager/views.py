from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

from noticeboard.apps.admanager.models import Ad
from noticeboard.apps.admanager.forms import CreateAdForm

from noticeboard.apps.profiles.models import Profile

def _get_customer(user):
    try:
        user_profile = Profile.objects.get(user=user)
        return Customer.objects.get(user_profile=user_profile)
    except Exception:
        raise

def homepage(request):
    """
    Shows all live ads of current user
    """
    ads = Ad.objects.filter(status=Ad.LIVE)
    context = {
        "ads": ads,
    }
    context = RequestContext(request, context)
    return render_to_response("homepage.html", context)


@login_required
def ads(request):
    """
    Lists ads of current user
    """
    ads = Ad.objects.filter(owner=_get_customer(request.user))
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

