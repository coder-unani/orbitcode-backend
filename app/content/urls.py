from django.urls import path

from . import views

app_name = "content"

urlpatterns = [
    path("", view=views.Index.as_view(), name="index"),
    path("video", view=views.VideoList.as_view(), name="video-list"),
    path("video/<int:pk>", view=views.VideoDetail.as_view(), name="video-detail"),
    path("video/<int:pk>/edit", view=views.VideoEdit.as_view(), name="video-edit"),
    path("genre", view=views.GenreList.as_view(), name="genre-list"),
    path("actor", view=views.ActorList.as_view(), name="actor-list"),
    path("staff", view=views.StaffList.as_view(), name="staff-list"),
]
