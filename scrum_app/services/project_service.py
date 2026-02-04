"""Project-related business logic."""

from django.db import transaction
from django.db.models import Q

from ..models import Project


class ProjectService:
    """Service class for project-related business logic."""

    @staticmethod
    def get_user_projects(user):
        """
        Get all projects where the user is owner OR a project member.

        Returns:
            QuerySet: Projects visible to the user
        """
        return (
            Project.objects.filter(Q(owner=user) | Q(members__user=user))
            .distinct()
            .order_by("-created_at")
        )

    @staticmethod
    def get_project_by_id(project_id):
        """
        Get a project by ID (authorization must be handled in the view).

        Returns:
            Project: The project instance
        """
        return Project.objects.get(pk=project_id)

    @staticmethod
    @transaction.atomic
    def create_project(form, owner):
        """Create a new project."""
        project = form.save(commit=False)
        project.owner = owner
        project.save()
        return project

    @staticmethod
    @transaction.atomic
    def update_project(form):
        """Update an existing project."""
        return form.save()

    @staticmethod
    @transaction.atomic
    def delete_project(project):
        """
        Delete a project.

        NOTE: Authorization should be enforced in the view.
        """
        project_name = project.name
        project.delete()
        return project_name

    @staticmethod
    def check_project_access(project, user):
        """
        Check if user has access to a project (owner OR member).

        NOTE: Project.is_member(user) already returns True for owner.
        """
        return project.is_member(user)