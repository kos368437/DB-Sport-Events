from django.db.models import PositiveIntegerField, Case, F, Sum, When
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.TextField(max_length=20, default='')
    surname = models.TextField(max_length=100, default='')
    name = models.TextField(max_length=100, default='')
    middle_name = models.TextField(max_length=100, default='', null=True)

    def __str__(self):
        return str(self.user) + ': ' + str(self.surname) + ' ' + str(self.name)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if not instance.profile:
        Profile.objects.create(user=instance)

    instance.profile.save()


class Coach(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, null=True)
    specialization = models.CharField(max_length=140, default='Тренер')
    description = models.TextField(max_length=280, default='')
    image = models.ImageField(null=True, default='media/coach_default.png')
    def __str__(self):
        return str(self.profile) + ': ' + str(self.specialization)


class Location(models.Model):
    name = models.CharField(max_length=200, default='')
    location_address = models.TextField(max_length=280, default='')
    max_seats = models.PositiveIntegerField(default=0)
    default_price = models.PositiveIntegerField(default=0)
    default_duration = models.DurationField(default='01:00:00')
    default_seats_count = models.PositiveIntegerField(default=0)
    default_coach = models.ForeignKey(Coach, on_delete=models.DO_NOTHING, null=True)

    def __str__(self):
        return str(self.name)


class SportEvent(models.Model):
    title = models.CharField(max_length=200)
    url = models.SlugField()
    announce_text = models.TextField(max_length=280, default='')
    description = models.TextField(default='')
    image = models.ImageField()
    event_date = models.DateTimeField(default=timezone.now)
    duration = models.DurationField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True)
    price = models.PositiveIntegerField()
    coach = models.ForeignKey(Coach, on_delete=models.DO_NOTHING, null=True)
    ticket_number = models.PositiveIntegerField()

    def __str__(self):
        return self.title

    @staticmethod
    def get_events():
        events = SportEvent.objects.all().select_related('location').select_related('coach').prefetch_related('reservation')
        events = events.values('title').order_by('title') \
                     .annotate(total_seats=Sum('reservation__seats_count')) \
                     .annotate(total_seats=F('ticket_number') - F('total_seats')) \
                     .annotate(total_seats=Case(
            When(total_seats=None, then=F('ticket_number')),
            default=F('total_seats'), output_field=PositiveIntegerField()
        )).values()
        return events
    def get_total_seats_count(self):
        events = SportEvent.objects.all().select_related('location').select_related('coach').prefetch_related('reservation').filter(id=self.id)
        total_seats = events.values('title').order_by('title') \
            .annotate(total_seats=Sum('reservation__seats_count')) \
            .annotate(total_seats=F('ticket_number') - F('total_seats')) \
            .annotate(total_seats=Case(
            When(total_seats=None, then=F('ticket_number')),
            default=F('total_seats'), output_field=PositiveIntegerField()
        )).values('total_seats').first()
        return total_seats['total_seats']
    @staticmethod
    def get_upcoming_events():
        events = SportEvent.get_events().filter(event_date__gte=timezone.now())
        return events


class ReservationStatusChoice(models.TextChoices):
    APPROVED = 'APP', _("Approved")
    NOTIFIED = 'NFY', _("Notified")
    REGISTERED = 'REG', _("Registered")


class Reservation(models.Model):
    seats_count = models.PositiveIntegerField()
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    event = models.ForeignKey(SportEvent, on_delete=models.CASCADE)
    status = models.CharField(
        choices=ReservationStatusChoice.choices,
        default=ReservationStatusChoice.REGISTERED,
        max_length=4,
        null=True
    )

    def __str__(self):
        return str(self.event) + ': ' + str(self.seats_count)
