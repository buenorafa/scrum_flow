from django import forms
from .models import Project


class ProjectForm(forms.ModelForm):
    """Form for creating and editing projects."""
    
    class Meta:
        model = Project
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o nome do projeto'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descreva seu projeto (opcional)',
                'rows': 4
            }),
        }
        labels = {
            'name': 'Nome do Projeto',
            'description': 'Descrição',
        }
