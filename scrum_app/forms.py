from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Project


class CustomUserCreationForm(UserCreationForm):
    """Formulário customizado de criação de usuário com campos adicionais."""

    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "seu@email.com"}
        ),
    )
    first_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Seu nome"}
        ),
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Seu sobrenome"}
        ),
    )

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ("email", "first_name", "last_name")
        widgets = {
            "username": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Escolha um usuário"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Escolha um usuário"}
        )
        self.fields["password1"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Digite sua senha"}
        )
        self.fields["password2"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Confirme sua senha"}
        )


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
