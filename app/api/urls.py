from django.urls import path, include

from .views import (
    Index, ActorPictureUpload, StaffPictureUpload
)

# content/video/{video_id}/watch : GET, POST, DELETE, PUT, PATCH
# content/video/{video_id}/thumbnail : GET, POST, DELETE, PUT, PATCH
# content/video/{video_id}/genre : GET, POST, DELETE, PUT, PATCH
# content/video/{video_id}/actor : GET, POST, DELETE, PUT, PATCH
# content/video/{video_id}/staff : GET, POST, DELETE, PUT, PATCH

urlpatterns = [
    path("auth/", include('rest_framework.urls'), name="auth"),
    path("", view=Index.as_view(), name="index"),
    path("uploads/actors/pictures", view=ActorPictureUpload.as_view(), name="upload-actor-image"),
    path("uploads/staffs/pictures", view=StaffPictureUpload.as_view(), name="upload-staff-image"),
]