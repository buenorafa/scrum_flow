"""
Services layer for business logic.
This module contains all business logic separated from views.
"""

from django.contrib.auth import login
from django.core.paginator import Paginator
from django.db import transaction

from .models import Project, ProjectMember


class UserService:
    """Service class for user-related business logic."""

    @staticmethod
    def register_user(form, request):
        """
        Register a new user and log them in.

        Args:
            form: CustomUserCreationForm with valid data
            request: HTTP request object

        Returns:
            User: The created user instance
        """
        user = form.save()
        login(request, user)
        return user


class ProjectService:
    """Service class for project-related business logic."""

    @staticmethod
    def get_user_projects(user):
        """
        Get all projects owned by a user.

        Args:
            user: User instance

        Returns:
            QuerySet: Projects owned by the user
        """
        return Project.objects.filter(owner=user)

    @staticmethod
    def get_project_by_id(project_id, owner):
        """
        Get a project by ID and owner.

        Args:
            project_id: Project primary key
            owner: User instance (project owner)

        Returns:
            Project: The project instance

        Raises:
            Project.DoesNotExist: If project not found
        """
        return Project.objects.get(pk=project_id, owner=owner)

    @staticmethod
    @transaction.atomic
    def create_project(form, owner):
        """
        Create a new project.

        Args:
            form: ProjectForm with valid data
            owner: User instance (project owner)

        Returns:
            Project: The created project instance
        """
        project = form.save(commit=False)
        project.owner = owner
        project.save()
        return project

    @staticmethod
    @transaction.atomic
    def update_project(form):
        """
        Update an existing project.

        Args:
            form: ProjectForm with valid data and instance

        Returns:
            Project: The updated project instance
        """
        return form.save()

    @staticmethod
    @transaction.atomic
    def delete_project(project):
        """
        Delete a project.

        Args:
            project: Project instance to delete

        Returns:
            str: The name of the deleted project
        """
        project_name = project.name
        project.delete()
        return project_name

    @staticmethod
    def check_project_access(project, user):
        """
        Check if user has access to view project members.

        Args:
            project: Project instance
            user: User instance

        Returns:
            bool: True if user is owner or member, False otherwise
        """
        return project.is_member(user) or project.is_owner(user)


class ProjectMemberService:
    """Service class for project member-related business logic."""

    @staticmethod
    def get_project_members_page(project, page_number, per_page=10):
        """
        Get paginated project members.

        Args:
            project: Project instance
            page_number: Page number to retrieve
            per_page: Number of members per page (default: 10)

        Returns:
            Page: Paginated members
        """
        members_list = list(project.members.select_related("user").all())
        paginator = Paginator(members_list, per_page)
        return paginator.get_page(page_number)

    @staticmethod
    @transaction.atomic
    def add_member_to_project(project, user):
        """
        Add a member to a project.

        Args:
            project: Project instance
            user: User instance to add as member

        Returns:
            ProjectMember: The created project member instance
        """
        return ProjectMember.objects.create(project=project, user=user)

    @staticmethod
    def get_project_member(member_id, project):
        """
        Get a project member by ID.

        Args:
            member_id: ProjectMember primary key
            project: Project instance

        Returns:
            ProjectMember: The project member instance

        Raises:
            ProjectMember.DoesNotExist: If member not found
        """
        return ProjectMember.objects.get(pk=member_id, project=project)

    @staticmethod
    @transaction.atomic
    def remove_member_from_project(member):
        """
        Remove a member from a project.

        Args:
            member: ProjectMember instance to remove

        Returns:
            str: The username of the removed member
        """
        username = member.user.username
        member.delete()
        return username
