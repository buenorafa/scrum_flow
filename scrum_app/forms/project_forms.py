"""Project-related forms."""

from django import forms
from django.contrib.auth.models import User

from ..models import Project


class ProjectForm(forms.ModelForm):
    """Form for creating and editing projects."""

    class Meta:
        model = Project
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Digite o nome do projeto",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Descreva seu projeto (opcional)",
                    "rows": 4,
                }
            ),
        }
        labels = {
            "name": "Nome do Projeto",
            "description": "Descrição",
        }


class AddMemberForm(forms.Form):
    """Form for adding a member to a project."""

    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label="Selecione o usuário",
        widget=forms.Select(attrs={"class": "form-select"}),
        empty_label="Escolha um usuário...",
    )

    def __init__(self, *args, **kwargs):
        project = kwargs.pop("project", None)
        super().__init__(*args, **kwargs)

        if project:
            # Exclude owner and existing members
            existing_member_ids = project.members.values_list("user_id", flat=True)
            self.fields["user"].queryset = User.objects.exclude(
                id__in=list(existing_member_ids) + [project.owner.id]
            )
