from django.contrib import admin
from django.urls import path, include
from accounts.views import login_page, register_page, dashboard_redirect
from jobs.views import home_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/accounts/", include("accounts.urls")),
    path("api/jobs/", include("jobs.urls")),  # API endpoints

    # HTML pages
    path("", home_view, name="home"),
    path("login/", login_page, name="login"),
    path("register/", register_page, name="register"),
    path("dashboard/", dashboard_redirect, name="dashboard"),
    
    # HTML student dashboard & job views
    path("", include("jobs.urls")),
]
