"""Forms for Task management."""

from django import forms

from scrum_app.models import Task, TaskComment


class TaskForm(forms.ModelForm):
    """Form for creating and editing tasks."""

    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "assigned_to",
            "status",
            "priority",
            "estimated_hours",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "assigned_to": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "estimated_hours": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.5",
                    "placeholder": "Ex: 2.5",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        project = kwargs.pop("project", None)
        super().__init__(*args, **kwargs)

        # Populate assigned_to with project members
        if project:
            from django.contrib.auth.models import User

            # Get all members of the project (owner + members)
            member_ids = list(project.members.values_list("user_id", flat=True)) + [
                project.owner.id
            ]
            members = User.objects.filter(id__in=member_ids).order_by("username")

            self.fields["assigned_to"].queryset = members
            self.fields["assigned_to"].choices = [("", "Nenhum responsável")] + [
                (user.id, user.username) for user in members
            ]


class TaskCommentForm(forms.ModelForm):
    """Form for adding comments to tasks."""

    class Meta:
        model = TaskComment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Escreva seu comentário...",
                }
            ),
        }
        labels = {
            "content": "Comentário",
        }


class TaskStatusUpdateForm(forms.ModelForm):
    """Form for quickly updating task status (for Kanban board)."""

    class Meta:
        model = Task
        fields = ["status"]
        widgets = {
            "status": forms.Select(attrs={"class": "form-select form-select-sm"}),
        }
