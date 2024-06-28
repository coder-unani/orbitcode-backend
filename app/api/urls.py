from django.urls import path, include

from .views import (
    Index, ActorPictureUpload, StaffPictureUpload, VideoThumbnailUpload, FindActor, FindStaff
)

urlpatterns = [
    path("auth/", include('rest_framework.urls'), name="auth"),
    path("", view=Index.as_view(), name="index"),
    path("uploads/actors/pictures", view=ActorPictureUpload.as_view(), name="upload-actor-image"),
    path("uploads/staffs/pictures", view=StaffPictureUpload.as_view(), name="upload-staff-image"),
    path("uploads/videos/thumbnails/", view=VideoThumbnailUpload.as_view(), name="upload-video-thumbnail"),
    # path("uploads/videos/thumbnails/pre", view=VideoThumbnailUpload.as_view(), name="upload-video-thumbnail"),
    path("find/actors", view=FindActor.as_view(), name="find-actors"),
    path("find/staffs", view=FindStaff.as_view(), name="find-actors"),
]
