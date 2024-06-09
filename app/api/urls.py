from django.urls import path, include

from .views import (
    Index,
    ApiVideoWatch,
    ApiVideoThumbnail,
    ApiVideoGenre,
)

# content/video/{video_id}/watch : GET, POST, DELETE, PUT, PATCH
# content/video/{video_id}/thumbnail : GET, POST, DELETE, PUT, PATCH
# content/video/{video_id}/genre : GET, POST, DELETE, PUT, PATCH
# content/video/{video_id}/actor : GET, POST, DELETE, PUT, PATCH
# content/video/{video_id}/staff : GET, POST, DELETE, PUT, PATCH

urlpatterns = [
    path("auth/", include('rest_framework.urls'), name="auth"),
    path("", view=Index.as_view(), name="index"),
    path("content/video/<int:video_id>/watch", view=ApiVideoWatch.as_view()),
    path("content/video/<int:video_id>/watch/<int:watch_id>", view=ApiVideoWatch.as_view()),
    path("content/video/<int:video_id>/thumbnail", view=ApiVideoThumbnail.as_view()),
    path("content/video/<int:video_id>/thumbnail/<int:thumbnail_id>", view=ApiVideoThumbnail.as_view()),
    path("content/video/<int:video_id>/genre", view=ApiVideoGenre.as_view()),
    path("content/video/<int:video_id>/genre/<int:genre_id>", view=ApiVideoGenre.as_view()),
]