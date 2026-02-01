"""Forms for UserStory management."""

from django import forms

from scrum_app.models import UserStory


class UserStoryForm(forms.ModelForm):
    """Form for creating and editing user stories."""

    # pylint: disable=missing-class-docstring
    class Meta:
        model = UserStory
        fields = [
            "title",
            "description",
            "as_a",
            "i_want",
            "so_that",
            "acceptance_criteria",
            "story_points",
            "priority",
            "status",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "as_a": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex: Como usuário do sistema",
                }
            ),
            "i_want": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex: Eu quero fazer login",
                }
            ),
            "so_that": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex: Para que eu possa acessar minhas informações",
                }
            ),
            "acceptance_criteria": forms.Textarea(
                attrs={"class": "form-control", "rows": 4}
            ),
            "story_points": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex: 1, 2, 3, 5, 8, 13...",
                }
            ),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }


class MoveUserStoryForm(forms.Form):
    """Form for moving a user story between backlogs."""

    MOVE_TO_CHOICES = [
        ("product", "Product Backlog"),
        ("sprint", "Sprint Backlog"),
    ]

    move_to = forms.ChoiceField(
        choices=MOVE_TO_CHOICES,
        widget=forms.RadioSelect,
        label="Mover para",
    )

    sprint = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Sprint",
        help_text="Selecione a sprint de destino (obrigatório se mover para Sprint Backlog)",
    )

    def __init__(self, *args, **kwargs):
        project = kwargs.pop("project", None)
        super().__init__(*args, **kwargs)

        if project:
            self.fields["sprint"].choices = [("", "Selecione uma sprint")] + [
                (sprint.id, str(sprint)) for sprint in project.sprints.all()
            ]

    def clean(self):
        cleaned_data = super().clean()
        move_to = cleaned_data.get("move_to")
        sprint = cleaned_data.get("sprint")

        if move_to == "sprint" and not sprint:
            raise forms.ValidationError(
                {
                    "sprint": "Você deve selecionar uma sprint ao mover para Sprint Backlog."
                }
            )

        return cleaned_data
