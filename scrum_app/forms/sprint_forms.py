from django import forms

from ..models import  Sprint


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
            "start_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}, format="%Y-%m-%d",),
            "end_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}, format="%Y-%m-%d",),
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