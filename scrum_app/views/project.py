"""Project CRUD views."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import ProjectForm
from ..models import Project
from ..services import ProjectService


@login_required
def project_list_view(request):
    """View to list all projects owned by the current user."""
    projects = ProjectService.get_user_projects(request.user)

    # Add pagination
    paginator = Paginator(projects, 10)  # 10 projects per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "projects/project_list.html", {"page_obj": page_obj})


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
            project = ProjectService.create_project(form, request.user)
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
            ProjectService.update_project(form)
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
        project_name = ProjectService.delete_project(project)
        messages.success(request, f'Projeto "{project_name}" excluído com sucesso!')
        return redirect("project_list")

    return render(request, "projects/project_confirm_delete.html", {"project": project})
