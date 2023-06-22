from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class Location(models.Model):
    def __str__(self):
        return ''

class Coach(models.Model):
    def __str__(self):
        return ''


class SportEvent(models.Model):
    title = models.CharField(max_length=200)
    url = models.SlugField()
    announce_text = models.TextField(max_length=280, default='')
    description = models.TextField(default='')
    image = models.ImageField()
    event_date = models.DateTimeField(default=timezone.now)
    duration = models.DurationField()
    # location = models.ForeignKey(Location, on_delete=models.CASCADE)
    price = models.PositiveIntegerField()
    # coach = models.ForeignKey(Coach, on_delete=models.CASCADE)
    ticket_number = models.PositiveIntegerField()


    def __str__(self):
        return self.title

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.TextField(max_length=20, default='')
    surname = models.TextField(max_length=100, default='')
    name = models.TextField(max_length=100, default='')
    middle_name = models.TextField(max_length=100, default='', null=True)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if not instance.profile:
        Profile.objects.create(user=instance)

    instance.profile.save()