from django.contrib.auth.models import User
from django.db import models


class Project(models.Model):
    """Model representing a project in the Scrum Flow application."""

    name = models.CharField(
        max_length=200, verbose_name="Nome", help_text="Nome do projeto"
    )
    description = models.TextField(
        verbose_name="Descrição", help_text="Descrição detalhada do projeto", blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de criação")
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="projects",
        verbose_name="Proprietário",
    )

    objects: models.Manager["Project"]
    members: models.Manager["ProjectMember"]

    class Meta:
        verbose_name = "Projeto"
        verbose_name_plural = "Projetos"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return str(self.name)

    def is_owner(self, user):
        """Check if the user is the owner of the project."""
        return self.owner == user

    def is_member(self, user):
        """Check if the user is a member of the project (including owner)."""
        if self.is_owner(user):
            return True
        return self.members.filter(user=user).exists()


class ProjectMember(models.Model):
    """Model representing a member of a project."""

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="members",
        verbose_name="Projeto",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="project_memberships",
        verbose_name="Usuário",
    )
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de entrada")

    objects: models.Manager["ProjectMember"]

    class Meta:
        verbose_name = "Membro do Projeto"
        verbose_name_plural = "Membros do Projeto"
        unique_together = ["project", "user"]
        ordering = ["joined_at"]

    def __str__(self) -> str:
        return (
            f"{self.user.username} - {self.project.name}"  # pylint: disable=no-member
        )
