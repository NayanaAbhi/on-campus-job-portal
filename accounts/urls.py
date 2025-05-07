from django.urls import path
from .views import login_page, register_page, dashboard_redirect, custom_logout
from django.contrib.auth.views import LogoutView
from .views import update_canvas_url
urlpatterns = [
    path('login/', login_page, name='login'),
    path('register/', register_page, name='register'),
    path('logout/', custom_logout, name='logout'),
    path('dashboard/', dashboard_redirect, name='dashboard'),
    path('calendar/update/', update_canvas_url, name='update-canvas-url'),
]
