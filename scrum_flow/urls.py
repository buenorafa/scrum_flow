from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from scrum_app.views import (
    register_view, 
    home_view,
    project_list_view,
    project_detail_view,
    project_create_view,
    project_update_view,
    project_delete_view,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home_view, name="home"),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("register/", register_view, name="register"),
    
    # Project URLs
    path("projects/", project_list_view, name="project_list"),
    path("projects/new/", project_create_view, name="project_create"),
    path("projects/<int:pk>/", project_detail_view, name="project_detail"),
    path("projects/<int:pk>/edit/", project_update_view, name="project_update"),
    path("projects/<int:pk>/delete/", project_delete_view, name="project_delete"),
]
