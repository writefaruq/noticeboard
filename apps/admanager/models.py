from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User

from noticeboard.apps.profiles.models import Profile
#from noticeboard.apps.payment.models import Invoice

###  =============== Ad Publishing stats when  Customer creates an Ad ================ ###

class Customer(models.Model):
    """
    Based on User Profile
    """
    user_profile = models.ForeignKey(Profile)

    def __unicode__(self):
        return self.user_profile.user.username


class AdCategory(models.Model):
    """
    Classifies Ads: mainly into Event, Service and Classifieds etc.
    can be inherited from separate classes
    """
    name = models.CharField(max_length=127)
    description = models.TextField()
    publish_rate = models.DecimalField(max_digits=7, decimal_places=2, default=0,
                                        help_text="GBP per day")
    class Meta:
        verbose_name_plural = "Ad Categories"

    def __unicode__(self):
        return self.name


class Ad(models.Model):
    """
    That appears on our notice board
    """
    title = models.CharField(max_length=127, help_text="Give a short crisp title")
    description = models.TextField(help_text="Provide a descripttion in 200 words")
    category = models.ForeignKey(AdCategory)
    created_at = models.DateTimeField(auto_now=True)
    last_updated = models.DateTimeField(auto_now_add=True)
    # owner
    owner = models.ForeignKey(Customer)  # who creates this
    # status
    (INACTIVE, UNDER_REVIEW, LIVE, EXPIRED) = range(4)
    STATUS_CHOICES = (
                      (INACTIVE, 'Inactive'),  # Not published yet
                      (UNDER_REVIEW, 'Under Review'),  # Not published yet
                      (LIVE, 'Live'),  # Available online
                      (EXPIRED, 'Expired') # publish time is over
                     )
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=INACTIVE, editable=False)

    def __unicode__(self):
        return "%s [%s]" %(self.title, self.get_status_display())

    def save(self, user=None, *args, **kwargs):
        if not self.id and user:
            profile = Profile.objects.get(user=user) ## TODO: replace tmporary test
            owner = Customer.objects.get_or_create(user_profile=profile)
            #import pdb; pdb.set_trace()
            self.owner = user
        super(Ad, self).save(*args, **kwargs)

    def go_live(self):
        self.status = self.LIVE
        self.save()

class AdStats(models.Model):
    """
    Holds statistics of Ad performance
    """
    ad = models.ForeignKey(Ad)
    live_from = models.DateTimeField(auto_now=True)
    expired_at = models.DateTimeField()
    visitor_likes = models.PositiveIntegerField(default=0, editable=False)
    vistor_comments = models.PositiveIntegerField(default=0, editable=False)

    class Meta:
        verbose_name_plural = "Ad Statistics"

    def __unicode__(self):
        return "<%s: starts:%s ends:%s>" %(self.ad, self.live_from, self.expired_at)


### After Ad is created Customer makes a request for publication which to be approved by an Admin ###

class ApprovalManager(models.Model):
    """
    Who approves our Ad
    """
    user_profile = models.ForeignKey(Profile)
    is_active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.user_profile.user.username


class PublishRequest(models.Model):
    """
    Records a request of publication of an Ad
    """
    ad = models.ForeignKey(Ad)
    start_from = models.DateTimeField()
    publish_day = models.PositiveIntegerField(help_text="publishing period in days")
    is_approved = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    signed_by = models.ForeignKey(ApprovalManager, editable=False)
    signed_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "%s [Approved]" %(self.ad)\
            if self.is_approved else "%s [Awaiting approval]" %(self.ad)

    def save(self, *args, **kwargs):
        if not self.id:
            profile = Profile.objects.get(pk=1) ## TODO: replace tmporary test
            self.signed_by = ApprovalManager.objects.create(user_profile=profile)
        super(PublishRequest, self).save(*args, **kwargs)
