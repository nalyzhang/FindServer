from django.contrib import admin

from .models import (Friend, FriendsList, Location,
                     Route, User)

admin.site.register(Friend)
admin.site.register(FriendsList)
admin.site.register(Location)
admin.site.register(Route)
admin.site.register(User)
