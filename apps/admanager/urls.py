from django.conf.urls.defaults import *
from apps.admanager.views import ads, create_ad, ad_stats

urlpatterns = patterns("",
    url(r"^$", ads, name="admanager_ads"),
    url(r"^create/$", create_ad, name="admanager_create_ad"),
    url(r"^stats/$", ad_stats, name="admanager_ad_stats"),
)