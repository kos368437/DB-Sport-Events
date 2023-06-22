from django.contrib import admin
from .models import SportEvent

class SportEventAdmin(admin.ModelAdmin):
    pass

admin.site.register(SportEvent, SportEventAdmin)