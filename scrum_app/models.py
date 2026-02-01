from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
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


class Sprint(models.Model):
    class Status(models.TextChoices):
        PLANNING = "PLANNING", "Planning"
        ACTIVE = "ACTIVE", "Active"
        CLOSED = "CLOSED", "Closed"

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="sprints",
        verbose_name="Projeto",
    )

    name = models.CharField(max_length=120, verbose_name="Nome")
    description = models.TextField(blank=True, verbose_name="Descrição")

    start_date = models.DateField(verbose_name="Data de início")
    end_date = models.DateField(verbose_name="Data de fim")

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PLANNING,
        verbose_name="Status",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de criação")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última atualização")

    objects: models.Manager["Sprint"]

    class Meta:
        verbose_name = "Sprint"
        verbose_name_plural = "Sprints"
        ordering = ["-start_date", "-created_at"]

    def __str__(self) -> str:
        return f"{self.name} - {self.project.name}"

    def clean(self):
        # validação de datas
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError(
                {"end_date": "A data de fim não pode ser anterior à data de início."}
            )

        # opcional (mas bem Scrum): só 1 sprint ACTIVE por projeto
        if self.status == self.Status.ACTIVE:
            qs = Sprint.objects.filter(project=self.project, status=self.Status.ACTIVE)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError(
                    {"status": "Já existe uma Sprint ativa neste projeto."}
                )
