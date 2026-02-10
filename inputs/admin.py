from django.contrib import admin
from .models import InputCategory, AgriculturalInput, GroupBuyPool, GroupBuyParticipant

admin.site.register(InputCategory)
admin.site.register(AgriculturalInput)
admin.site.register(GroupBuyPool)
admin.site.register(GroupBuyParticipant)