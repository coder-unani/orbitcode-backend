from django.urls import path

from . import views

app_name = "builder"

urlpatterns = [
    path("", view=views.Index.as_view(), name="index"),
    path("collect/netflix/", view=views.CollectNetflix.as_view(), name="collect-netflix"),
    path("collect/netflix/boxoffice", view=views.CollectNetflixBoxoffice.as_view(), name="collect-netflix-boxoffice"),
    path("collect/disney/", view=views.CollectDisney.as_view(), name="collect-disney"),
    path("collect/tving/", view=views.CollectTving.as_view(), name="collect-tving"),
    path("collect/tving/boxoffice", view=views.CollectTvingBoxoffice.as_view(), name="collect-tving-boxoffice"),
]
