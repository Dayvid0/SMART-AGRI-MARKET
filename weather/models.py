from django.db import models

class WeatherAlert(models.Model):
    """
    Weather alerts and warnings for farmers
    """
    ALERT_TYPES = (
        ('rain', 'Heavy Rain'),
        ('drought', 'Drought Warning'),
        ('storm', 'Storm Warning'),
        ('frost', 'Frost Warning'),
        ('heatwave', 'Heatwave'),
    )
    
    SEVERITY_LEVELS = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )
    
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    affected_regions = models.CharField(max_length=300, help_text="Comma-separated regions")
    
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    recommendations = models.TextField(help_text="What farmers should do")
    
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.title}"
    
    class Meta:
        verbose_name = "Weather Alert"
        verbose_name_plural = "Weather Alerts"
        ordering = ['-created_at']


class PlantingSeason(models.Model):
    """
    Planting season recommendations based on climate data
    """
    crop_name = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    
    best_planting_start = models.DateField()
    best_planting_end = models.DateField()
    
    expected_harvest_start = models.DateField()
    expected_harvest_end = models.DateField()
    
    rainfall_required = models.CharField(max_length=100, help_text="e.g., 800-1200mm")
    temperature_range = models.CharField(max_length=100, help_text="e.g., 20-30°C")
    
    planting_tips = models.TextField()
    
    def __str__(self):
        return f"{self.crop_name} - {self.region}"
    
    class Meta:
        verbose_name = "Planting Season"
        verbose_name_plural = "Planting Seasons"


class PestAlert(models.Model):
    """
    Pest and disease outbreak alerts
    """
    pest_name = models.CharField(max_length=200)
    affected_crops = models.CharField(max_length=300, help_text="Comma-separated crops")
    affected_regions = models.CharField(max_length=300)
    
    description = models.TextField()
    symptoms = models.TextField(help_text="How to identify the pest/disease")
    
    severity = models.CharField(
        max_length=20,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
        default='medium'
    )
    
    control_measures = models.TextField(help_text="How to control/prevent")
    recommended_products = models.TextField(blank=True, help_text="Recommended pesticides")
    
    image = models.ImageField(upload_to='pests/', blank=True, null=True)
    
    reported_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.pest_name} - {self.affected_regions}"
    
    class Meta:
        verbose_name = "Pest Alert"
        verbose_name_plural = "Pest Alerts"
        ordering = ['-reported_date']