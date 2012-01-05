from datetime import datetime
from django import forms
from django.utils.translation import ugettext_lazy as _, ugettext

from noticeboard.apps.profiles.models import Profile
from noticeboard.apps.admanager.models import Ad, AdCategory, Customer, PublishRequest

class CreateAdForm(forms.Form):
    """
    Need to redirect form after save
    """

    title = forms.CharField(
        label = _("Title"),
        max_length = 50,
        widget = forms.TextInput()
    )
    description = forms.CharField(
        label = _("Description"),
        max_length = 1000,
        widget = forms.Textarea()
    )
    category = forms.ModelChoiceField(
        label = _("Category"),
        queryset = AdCategory.objects.all()
    )
    send_for_approval = forms.BooleanField(
        label = _("Send for approval?"),
    )

    def __init__(self, *args, **kwargs):
        super(CreateAdForm, self).__init__(*args, **kwargs)

    def save(self, user):

        profile = Profile.objects.get(user=user)
        # get the customer and create an ad
        (self.owner, _) = Customer.objects.get_or_create(user_profile=profile)
        (self.ad, _) = Ad.objects.get_or_create(title=self.cleaned_data['title'],
                     description=self.cleaned_data['description'],
                     category=self.cleaned_data['category'],
                     owner=self.owner)
        # sent for approval
        if self.cleaned_data['send_for_approval']:
            publish = PublishRequest.objects.get_or_create(
                        ad=self.ad,
                        start_from = datetime.now(),
                        publish_day = 7
                      )
            self.ad.sent_for_approval()

