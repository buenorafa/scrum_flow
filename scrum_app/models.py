# pylint: disable=missing-module-docstring
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

    # pylint: disable=missing-class-docstring
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

    # pylint: disable=missing-class-docstring
    class Meta:
        verbose_name = "Membro do Projeto"
        verbose_name_plural = "Membros do Projeto"
        unique_together = ["project", "user"]
        ordering = ["joined_at"]

    def __str__(self) -> str:
        return (
            f"{self.user.username} - {self.project.name}"  # pylint: disable=no-member
        )


# pylint: disable=missing-class-docstring
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


class ProductBacklog(models.Model):
    """Model representing a product backlog for a project."""

    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name="product_backlog",
        verbose_name="Projeto",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de criação")

    objects: models.Manager["ProductBacklog"]

    class Meta:
        verbose_name = "Product Backlog"
        verbose_name_plural = "Product Backlogs"

    def __str__(self) -> str:
        return f"Product Backlog - {self.project.name}"


class SprintBacklog(models.Model):
    """Model representing a sprint backlog for a sprint."""

    sprint = models.OneToOneField(
        Sprint,
        on_delete=models.CASCADE,
        related_name="sprint_backlog",
        verbose_name="Sprint",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de criação")

    objects: models.Manager["SprintBacklog"]

    class Meta:
        verbose_name = "Sprint Backlog"
        verbose_name_plural = "Sprint Backlogs"

    def __str__(self) -> str:
        return f"Sprint Backlog - {self.sprint.name}"


class UserStory(models.Model):
    """Model representing a user story in the Scrum Flow application."""

    class Priority(models.TextChoices):
        LOW = "LOW", "Baixa"
        MEDIUM = "MEDIUM", "Média"
        HIGH = "HIGH", "Alta"
        CRITICAL = "CRITICAL", "Crítica"

    class Status(models.TextChoices):
        TODO = "TODO", "A Fazer"
        IN_PROGRESS = "IN_PROGRESS", "Em Progresso"
        DONE = "DONE", "Concluído"

    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(verbose_name="Descrição")

    # User story format: "Como [tipo de usuário], eu quero [objetivo] para [benefício]"
    as_a = models.CharField(
        max_length=200,
        verbose_name="Como (tipo de usuário)",
        help_text="Ex: Como usuário do sistema",
        blank=True,
    )
    i_want = models.CharField(
        max_length=200,
        verbose_name="Eu quero",
        help_text="Ex: Eu quero fazer login",
        blank=True,
    )
    so_that = models.CharField(
        max_length=200,
        verbose_name="Para que",
        help_text="Ex: Para que eu possa acessar o sistema",
        blank=True,
    )

    acceptance_criteria = models.TextField(
        verbose_name="Critérios de Aceitação",
        blank=True,
        help_text="Critérios para considerar esta história como concluída",
    )

    story_points = models.IntegerField(
        verbose_name="Story Points",
        null=True,
        blank=True,
        help_text="Estimativa de esforço (Fibonacci: 1, 2, 3, 5, 8, 13...)",
    )

    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        verbose_name="Prioridade",
    )

    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.TODO,
        verbose_name="Status",
    )

    product_backlog = models.ForeignKey(
        ProductBacklog,
        on_delete=models.CASCADE,
        related_name="user_stories",
        verbose_name="Product Backlog",
        null=True,
        blank=True,
    )

    sprint_backlog = models.ForeignKey(
        SprintBacklog,
        on_delete=models.CASCADE,
        related_name="user_stories",
        verbose_name="Sprint Backlog",
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de criação")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última atualização")

    objects: models.Manager["UserStory"]

    class Meta:
        verbose_name = "User Story"
        verbose_name_plural = "User Stories"
        ordering = ["-priority", "-created_at"]

    def __str__(self) -> str:
        return str(self.title)

    def clean(self):
        # Uma user story deve estar em apenas um backlog
        if self.product_backlog and self.sprint_backlog:
            raise ValidationError(
                "Uma User Story não pode estar em Product Backlog e Sprint Backlog simultaneamente."
            )

        # Uma user story deve estar em pelo menos um backlog
        if not self.product_backlog and not self.sprint_backlog:
            raise ValidationError(
                "Uma User Story deve estar associada a um Product Backlog ou Sprint Backlog."
            )

    def move_to_sprint(self, sprint):
        """Move user story from product backlog to sprint backlog."""
        sprint_backlog, _ = SprintBacklog.objects.get_or_create(sprint=sprint)
        self.product_backlog = None
        self.sprint_backlog = sprint_backlog
        self.save()

    def move_to_product_backlog(self, project):
        """Move user story from sprint backlog to product backlog."""
        product_backlog, _ = ProductBacklog.objects.get_or_create(project=project)
        self.sprint_backlog = None
        self.product_backlog = product_backlog
        self.save()


class Task(models.Model):
    """Model representing a task within a user story."""

    class Status(models.TextChoices):
        TODO = "TODO", "A Fazer"
        IN_PROGRESS = "IN_PROGRESS", "Em Progresso"
        DONE = "DONE", "Concluído"

    class Priority(models.TextChoices):
        LOW = "LOW", "Baixa"
        MEDIUM = "MEDIUM", "Média"
        HIGH = "HIGH", "Alta"

    user_story = models.ForeignKey(
        UserStory,
        on_delete=models.CASCADE,
        related_name="tasks",
        verbose_name="User Story",
    )

    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(verbose_name="Descrição", blank=True)

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
        verbose_name="Responsável",
    )

    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.TODO,
        verbose_name="Status",
    )

    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        verbose_name="Prioridade",
    )

    estimated_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Horas Estimadas",
        help_text="Estimativa de horas para completar a task",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de criação")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última atualização")

    objects: models.Manager["Task"]

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        ordering = ["-priority", "status", "-created_at"]

    def __str__(self) -> str:
        return str(self.title)


class TaskComment(models.Model):
    """Model representing a comment on a task."""

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Task",
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="task_comments",
        verbose_name="Autor",
    )

    content = models.TextField(verbose_name="Comentário")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de criação")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última atualização")

    objects: models.Manager["TaskComment"]

    class Meta:
        verbose_name = "Comentário"
        verbose_name_plural = "Comentários"
        ordering = ["created_at"]

    def __str__(self) -> str:
        # pylint: disable=no-member
        return f"Comentário de {self.author.username} em {self.task.title}"
