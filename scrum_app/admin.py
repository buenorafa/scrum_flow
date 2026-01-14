from django.contrib import admin

from .models import Project, ProjectMember


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin configuration for Project model."""

    list_display = ["name", "owner", "created_at"]
    list_filter = ["created_at", "owner"]
    search_fields = ["name", "description"]
    readonly_fields = ["created_at"]

    fieldsets = (
        ("Informações Principais", {"fields": ("name", "description", "owner")}),
        (
            "Informações do Sistema",
            {"fields": ("created_at",), "classes": ("collapse",)},
        ),
    )


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    """Admin configuration for ProjectMember model."""

    list_display = ["user", "project", "joined_at"]
    list_filter = ["joined_at", "project"]
    search_fields = ["user__username", "project__name"]
    readonly_fields = ["joined_at"]

    fieldsets = (
        ("Informações do Membro", {"fields": ("project", "user")}),
        (
            "Informações do Sistema",
            {"fields": ("joined_at",), "classes": ("collapse",)},
        ),
    )
