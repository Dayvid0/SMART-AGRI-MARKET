from django.contrib import admin
from .models import WeatherAlert, PlantingSeason, PestAlert

class WeatherAlertAdmin(admin.ModelAdmin):
    list_display = ['title', 'alert_type', 'severity', 'start_date', 'is_active']
    list_filter = ['alert_type', 'severity', 'is_active']

admin.site.register(WeatherAlert, WeatherAlertAdmin)
admin.site.register(PlantingSeason)
admin.site.register(PestAlert)