from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from scrum_app.views import (
    home_view,
    project_add_member_view,
    project_create_view,
    project_delete_view,
    project_detail_view,
    project_list_view,
    project_members_view,
    project_remove_member_view,
    project_update_view,
    register_view,
    sprint_list,
    sprint_create,
    sprint_detail,
    sprint_update,
    sprint_close,
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
    # Project Members URLs
    path("projects/<int:pk>/members/", project_members_view, name="project_members"),
    path(
        "projects/<int:pk>/members/add/",
        project_add_member_view,
        name="project_add_member",
    ),
    path(
        "projects/<int:pk>/members/<int:member_id>/remove/",
        project_remove_member_view,
        name="project_remove_member",
    ),

    # Sprints
    path(
        "projects/<int:project_id>/sprints/",
        sprint_list,
        name="sprint_list",
    ),
    path(
        "projects/<int:project_id>/sprints/new/",
        sprint_create,
        name="sprint_create",
    ),
    path(
        "sprints/<int:sprint_id>/",
        sprint_detail,
        name="sprint_detail",
    ),
    path(
        "sprints/<int:sprint_id>/edit/",
        sprint_update,
        name="sprint_update",
    ),
    path(
        "sprints/<int:sprint_id>/close/",
        sprint_close,
        name="sprint_close",)
]