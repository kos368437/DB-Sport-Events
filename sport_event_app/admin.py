from django.contrib import admin
from .models import SportEvent, Profile, Coach, Location, Reservation


class SportEventAdmin(admin.ModelAdmin):
    pass


class ProfileAdmin(admin.ModelAdmin):
    pass


class CoachAdmin(admin.ModelAdmin):
    pass


class LocationAdmin(admin.ModelAdmin):
    pass


class ReservationAdmin(admin.ModelAdmin):
    pass


admin.site.register(SportEvent, SportEventAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Coach, CoachAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Reservation, ReservationAdmin)
