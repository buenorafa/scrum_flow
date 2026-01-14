from django import forms
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AddMemberForm, ProjectForm
from .models import Project, ProjectMember


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


def register_view(request):
    """View para registro de novos usuários."""
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                f"Bem-vindo(a), {user.username}! Sua conta foi criada com sucesso.",
            )
            return redirect("home")
        else:
            messages.error(request, "Por favor, corrija os erros abaixo.")
    else:
        form = CustomUserCreationForm()

    return render(request, "registration/register.html", {"form": form})


@login_required
def home_view(request):
    """View da página inicial."""
    return render(request, "home.html")


# Project CRUD Views


@login_required
def project_list_view(request):
    """View to list all projects owned by the current user."""
    projects = Project.objects.filter(owner=request.user)
    return render(request, "projects/project_list.html", {"projects": projects})


@login_required
def project_detail_view(request, pk):
    """View to display project details."""
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    return render(request, "projects/project_detail.html", {"project": project})


@login_required
def project_create_view(request):
    """View to create a new project."""
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            messages.success(request, f'Projeto "{project.name}" criado com sucesso!')
            return redirect("project_detail", pk=project.pk)
    else:
        form = ProjectForm()

    return render(
        request,
        "projects/project_form.html",
        {"form": form, "title": "Novo Projeto", "button_text": "Criar Projeto"},
    )


@login_required
def project_update_view(request, pk):
    """View to update an existing project."""
    project = get_object_or_404(Project, pk=pk, owner=request.user)

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(
                request, f'Projeto "{project.name}" atualizado com sucesso!'
            )
            return redirect("project_detail", pk=project.pk)
    else:
        form = ProjectForm(instance=project)

    return render(
        request,
        "projects/project_form.html",
        {
            "form": form,
            "title": "Editar Projeto",
            "button_text": "Salvar Alterações",
            "project": project,
        },
    )


@login_required
def project_delete_view(request, pk):
    """View to delete a project."""
    project = get_object_or_404(Project, pk=pk, owner=request.user)

    if request.method == "POST":
        project_name = project.name
        project.delete()
        messages.success(request, f'Projeto "{project_name}" excluído com sucesso!')
        return redirect("project_list")

    return render(request, "projects/project_confirm_delete.html", {"project": project})


# Project Members Views


@login_required
def project_members_view(request, pk):
    """View to list all members of a project with pagination."""
    project = get_object_or_404(Project, pk=pk)

    # Check if user is member or owner
    if not project.is_member(request.user) and not project.is_owner(request.user):
        messages.error(
            request, "Você não tem permissão para ver os membros deste projeto."
        )
        return redirect("project_list")

    # Get all members including owner
    members_list = list(project.members.select_related("user").all())

    # Paginate members
    paginator = Paginator(members_list, 10)  # 10 members per page
    page_number = request.GET.get("page")
    members_page = paginator.get_page(page_number)

    return render(
        request,
        "projects/project_members.html",
        {
            "project": project,
            "members_page": members_page,
            "is_owner": project.is_owner(request.user),
        },
    )


@login_required
def project_add_member_view(request, pk):
    """View to add a member to a project. Only owner can add members."""
    project = get_object_or_404(Project, pk=pk, owner=request.user)

    if request.method == "POST":
        form = AddMemberForm(request.POST, project=project)
        if form.is_valid():
            user = form.cleaned_data["user"]
            ProjectMember.objects.create(project=project, user=user)
            messages.success(request, f"{user.username} foi adicionado ao projeto!")
            return redirect("project_members", pk=project.pk)
    else:
        form = AddMemberForm(project=project)

    return render(
        request,
        "projects/project_add_member.html",
        {
            "project": project,
            "form": form,
        },
    )


@login_required
def project_remove_member_view(request, pk, member_id):
    """View to remove a member from a project. Only owner can remove members."""
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    member = get_object_or_404(ProjectMember, pk=member_id, project=project)

    if request.method == "POST":
        username = member.user.username
        member.delete()
        messages.success(request, f"{username} foi removido do projeto!")
        return redirect("project_members", pk=project.pk)

    return render(
        request,
        "projects/project_remove_member.html",
        {
            "project": project,
            "member": member,
        },
    )
