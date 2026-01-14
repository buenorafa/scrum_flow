from django.contrib import admin
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin configuration for Project model."""
    
    list_display = ['name', 'owner', 'created_at']
    list_filter = ['created_at', 'owner']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Informações Principais', {
            'fields': ('name', 'description', 'owner')
        }),
        ('Informações do Sistema', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

