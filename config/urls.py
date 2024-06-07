from django.urls import path, include

from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path("login/", LoginView.as_view(template_name="auth/login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("admin/", admin.site.urls),
    path("api/", include('app.api.urls'), name='api'),
    path("builder/", include('app.builder.urls'), name='builder'),
    # path("content/", include('content.urls'), name='content'),
    path("dashboard/", include('app.dashboard.urls'), name='dashboard'),
]
