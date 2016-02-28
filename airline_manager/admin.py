from django.contrib import admin

from .models import Airline, PlaneType, Plane, Airport, Alliance

admin.site.register(Airline)
admin.site.register(PlaneType)
admin.site.register(Plane)
admin.site.register(Airport)
admin.site.register(Alliance)