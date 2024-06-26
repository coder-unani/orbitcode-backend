from django.contrib import admin

# Register your models here.
from app.database.models import (
    Video,
    Actor,
    Staff,
    Genre,
    Production,
    VideoActor,
    VideoStaff,
    VideoGenre,
    VideoProduction,
    VideoThumbnail,
    VideoPlatform,
    CountryCode
)

admin.site.register(Video)
admin.site.register(Actor)
admin.site.register(Staff)
admin.site.register(Genre)
admin.site.register(Production)
admin.site.register(VideoActor)
admin.site.register(VideoStaff)
admin.site.register(VideoGenre)
admin.site.register(VideoProduction)
admin.site.register(VideoThumbnail)
admin.site.register(VideoPlatform)
admin.site.register(CountryCode)
