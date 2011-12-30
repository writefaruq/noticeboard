from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User

from noticeboard.apps.profiles.models import Profile

###  =============== Step 1: Customer creates an Ad  ================ ###

class Customer(models.Model):
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
    owner = models.ForeignKey(Customer, editable=False)  # who creates this
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
        return self.title

    def save(self, *args, **kwargs):
        if not self.id:
            profile = Profile.objects.get(pk=1) ## TODO: replace tmporary test
            owner = Customer.objects.create(user_profile=profile)
            self.owner = owner
        super(Ad, self).save(*args, **kwargs)

class AdStats(models.Model):
    """
    Holds statistics of Ad performance
    """
    ad = models.ForeignKey(Ad)
    live_from = models.DateTimeField(auto_now=True)
    expired_at = models.DateTimeField()
    visitor_likes = models.PositiveIntegerField(default=0, help_text="keeps track of Like")
    vistor_comments = models.PositiveIntegerField(default=0, help_text="keeps track of comments")

    def __unicode__(self):
        return "<%s: Starts:%s Ends:>" %(self.ad, self.live_from, self.expired_at)


### ================= Step 2: Customer makes a request for publication ======== ###

class PublishRequest(models.Model):
    """
    Records a request of publication of an Ad
    """
    ad = models.ForeignKey(Ad)
    start_from = models.DateTimeField()
    publish_day = models.PositiveIntegerField(help_text="publishing period in days")

    def __unicode__(self):
        return "%s: dispay %s days" %(self.ad, self.publish_day)


### === Step 4: Approved Ads need payment by Customer ======= #####

class PublishFeePayment(models.Model):
    """
    Holds the details of payment
    """
    ad = models.ForeignKey(Ad)
    amount_due = models.DecimalField(max_digits=7, decimal_places=2, default=0,
                                        help_text="publish_rate * publish_day")
    # should be called publishing charge
    amount_paid = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    paid_at = models.DateTimeField(auto_now=True)
    # derived shortcuts
    is_full_paid = (amount_paid == amount_due)

    def __unicode__(self):
        return "%s due: %s" %(self.ad, (self.amount_paid - self.amount_due))


    def save(self, *args, **kwargs):
        if self.is_full_paid:
            self.ad.status = self.ad.LIVE
            self.ad.save()
            adstats = AdStats.object.create(
                            ad=self.ad,
                            expired_at=(self.paid_at +
                                time_delta(day=amount_paid/ad.category.publish_rate))
                      )
        super(PublishFeePayment, self).save(*args, **kwargs)


### Step 3: Approval manager approves/declines the request for publication  ###

class ApprovalManager(models.Model):
    """
    Who approves our Ad
    """
    user_profile = models.ForeignKey(Profile)
    is_active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.user_profile.user.username


class PublishApproval(models.Model):
    """
    Where pusblish request is signed by an Approval manager
    """
    publish_request = models.ForeignKey(PublishRequest)
    is_approved = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    signed_by = models.ForeignKey(ApprovalManager, editable=False)
    signed_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "%s: -> Approved" %(self.publish_request.ad)\
            if self.is_approved else "%s: Awaiting approval" %(self.publish_request.ad)

    def save(self, *args, **kwargs):
        if not self.id:
            profile = Profile.objects.get(pk=1) ## TODO: replace tmporary test
            signed_by = ApprovalManager.objects.create(user_profile=profile)
            self.signed_by = signed_by
            # side effects o approval
            ad = self.publish_request.ad
            amount_due = ad.category.publish_rate * self.publish_request.publish_day
            payment = PublishFeePayment.objects.create(
                                ad=self.publish_request.ad,
                                amount_due=amount_due)
        super(PublishApproval, self).save(*args, **kwargs)

### === Step 5: Paid Ads goes live and shows stats  ======= ###



