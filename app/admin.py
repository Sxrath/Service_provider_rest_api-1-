from django.contrib import admin
from .import models
# Register your models here.
admin.site.register(models.CustomUser)
admin.site.register(models.Category)
admin.site.register(models.Feedback)
admin.site.register(models.Locations)
admin.site.register(models.Booking)
admin.site.register(models.ServiceProvider)
admin.site.register(models.ServiceProviderprofile)
admin.site.register(models.Message)
admin.site.register(models.Payment)
admin.site.register(models.Report)
admin.site.register(models.FeedbackRespond)
