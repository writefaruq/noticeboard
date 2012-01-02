from django import forms
from django.utils.translation import ugettext_lazy as _, ugettext

from noticeboard.apps.profiles.models import Profile
from noticeboard.apps.admanager.models import Ad, AdCategory, Customer

class CreateAdForm(forms.Form):

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

    def __init__(self, *args, **kwargs):
        super(CreateAdForm, self).__init__(*args, **kwargs)

    def save(self, user):

        profile = Profile.objects.get(user=user)
        # get the customer
        (self.owner, _) = Customer.objects.get_or_create(user_profile=profile)
        self.ad = Ad(title=self.cleaned_data['title'],
                     description=self.cleaned_data['description'],
                     category=self.cleaned_data['category'],
                     owner=self.owner)
        self.ad.save()
