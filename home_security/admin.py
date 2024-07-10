from django.contrib import admin

from .models import Apartment, Building, Entrance, Event, Notification, User

admin.site.register([Building, Entrance, Apartment, Event, Notification, User])
