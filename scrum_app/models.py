from django.db import models
from django.contrib.auth.models import User


class Project(models.Model):
    """Model representing a project in the Scrum Flow application."""
    
    name = models.CharField(
        max_length=200,
        verbose_name="Nome",
        help_text="Nome do projeto"
    )
    description = models.TextField(
        verbose_name="Descrição",
        help_text="Descrição detalhada do projeto",
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de criação"
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='projects',
        verbose_name="Proprietário"
    )
    
    class Meta:
        verbose_name = "Projeto"
        verbose_name_plural = "Projetos"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name

