"""Views package for scrum_app."""

from .auth import home_view, register_view
from .project import (
    project_create_view,
    project_delete_view,
    project_detail_view,
    project_list_view,
    project_update_view,
)
from .project_member import (
    project_add_member_view,
    project_members_view,
    project_remove_member_view,
)

from .sprint import (
    sprint_list_view,
    sprint_detail_view,
    sprint_create_view,
    sprint_update_view, 
    sprint_close_view
)

__all__ = [
    # Auth views
    "register_view",
    "home_view",
    # Project views
    "project_list_view",
    "project_detail_view",
    "project_create_view",
    "project_update_view",
    "project_delete_view",
    # Project member views
    "project_members_view",
    "project_add_member_view",
    "project_remove_member_view",
    # Sprint views
    "sprint_list_view",
    "sprint_detail_view",
    "sprint_create_view",
    "sprint_update_view", 
    "sprint_close_view",
]
