"""Project-related forms."""

from django import forms
from django.contrib.auth.models import User

from ..models import Project, Sprint


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

class SprintForm(forms.ModelForm):
    """Form for creating and editing sprints."""

    class Meta:
        model = Sprint
        fields = ["name", "description", "start_date", "end_date", "status"]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Digite o nome da sprint (ex: Sprint 1)",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Descrição da sprint (opcional)",
                    "rows": 4,
                }
            ),
            "start_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "end_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }

        labels = {
            "name": "Nome da Sprint",
            "description": "Descrição",
            "start_date": "Data de Início",
            "end_date": "Data de Fim",
            "status": "Status",
        }

    def clean(self):
        cleaned = super().clean()
        start_date = cleaned.get("start_date")
        end_date = cleaned.get("end_date")

        if start_date and end_date and end_date < start_date:
            self.add_error("end_date", "A data de fim não pode ser anterior à data de início.")

        return cleaned