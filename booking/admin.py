from django.contrib import admin
from .models import Appointment, BlockedTime, Client, Service

admin.site.register(Service)
admin.site.register(Client)
admin.site.register(Appointment)
admin.site.register(BlockedTime)
