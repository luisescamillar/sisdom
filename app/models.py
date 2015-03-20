from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    # This line is required. Links UserProfile to a User model instance.
    user = models.OneToOneField(User)

    # The additional attributes we wish to include.
    twitter = models.CharField(blank=True, max_length=15)
    numcel = models.CharField(blank=True, max_length=10)
    abre = models.BooleanField(default=False)
    recibemsg = models.BooleanField(default=False)

    # Override the __unicode__() method to return out something meaningful!
    def __unicode__(self):
        return self.user.username

class Config(models.Model):
    youtube = models.CharField(blank=True, max_length=254)
    urlcam = models.CharField(blank=True, max_length=300)