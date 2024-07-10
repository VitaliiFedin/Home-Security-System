from django.contrib import admin

from .models import Apartment, Building, Entrance, Event, User

admin.site.register([Building, Entrance, Apartment, Event, User])
