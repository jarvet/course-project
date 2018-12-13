from django.contrib import admin

# Register your models here.
from .models import UserProfile, Tag, Schedule, Note, Location, Friendship, Filter, Comment, Area

admin.site.register(UserProfile)
admin.site.register(Tag)
admin.site.register(Schedule)
admin.site.register(Note)
admin.site.register(Location)
admin.site.register(Friendship)
admin.site.register(Filter)
admin.site.register(Comment)
admin.site.register(Area)
