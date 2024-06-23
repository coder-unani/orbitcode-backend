from django.contrib import admin

# Register your models here.
from app.database.models import (
    Actor,
    Genre,
    Staff,
    Video,
    VideoActor,
    VideoGenre,
    VideoStaff,
    VideoThumbnail,
    VideoWatch,
    CountryCode
)

admin.site.register(Actor)
admin.site.register(Genre)
admin.site.register(Staff)
admin.site.register(Video)
admin.site.register(VideoActor)
admin.site.register(VideoGenre)
admin.site.register(VideoStaff)
admin.site.register(VideoThumbnail)
admin.site.register(VideoWatch)
admin.site.register(CountryCode)