# pylint: disable=missing-module-docstring
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
)
from scrum_app.views.sprint import (
    sprint_close_view,
    sprint_create_view,
    sprint_detail_view,
    sprint_list_view,
    sprint_update_view,
)
from scrum_app.views.user_story import (
    product_backlog_view,
    sprint_backlog_view,
    user_story_create_for_product_backlog,
    user_story_create_for_sprint_backlog,
    user_story_delete_view,
    user_story_detail_view,
    user_story_move_view,
    user_story_update_view,
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
        sprint_list_view,
        name="sprint_list",
    ),
    path(
        "projects/<int:project_id>/sprints/new/",
        sprint_create_view,
        name="sprint_create",
    ),
    path(
        "sprints/<int:sprint_id>/",
        sprint_detail_view,
        name="sprint_detail",
    ),
    path(
        "sprints/<int:sprint_id>/edit/",
        sprint_update_view,
        name="sprint_update",
    ),
    path(
        "sprints/<int:sprint_id>/close/",
        sprint_close_view,
        name="sprint_close",
    ),
    # Product Backlog URLs
    path(
        "projects/<int:project_pk>/backlog/",
        product_backlog_view,
        name="product_backlog",
    ),
    path(
        "projects/<int:project_pk>/backlog/user-story/new/",
        user_story_create_for_product_backlog,
        name="user_story_create_product",
    ),
    # Sprint Backlog URLs
    path(
        "sprints/<int:sprint_pk>/backlog/",
        sprint_backlog_view,
        name="sprint_backlog",
    ),
    path(
        "sprints/<int:sprint_pk>/backlog/user-story/new/",
        user_story_create_for_sprint_backlog,
        name="user_story_create_sprint",
    ),
    # User Story URLs
    path(
        "user-stories/<int:pk>/",
        user_story_detail_view,
        name="user_story_detail",
    ),
    path(
        "user-stories/<int:pk>/edit/",
        user_story_update_view,
        name="user_story_update",
    ),
    path(
        "user-stories/<int:pk>/delete/",
        user_story_delete_view,
        name="user_story_delete",
    ),
    path(
        "user-stories/<int:pk>/move/",
        user_story_move_view,
        name="user_story_move",
    ),
]
