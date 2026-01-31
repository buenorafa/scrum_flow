from django import forms
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.http import Http404



from ..forms.sprint_forms import  SprintForm
from ..models import Project, Sprint



# Sprint

def _get_project_or_404(project_id, user):
    project = get_object_or_404(Project, id=project_id)
    if not project.is_member(user):
        raise Http404("Projeto não encontrado.")  # “esconde” para não-membros
    return project


def _get_sprint_or_404(sprint_id, user):
    sprint = get_object_or_404(Sprint, id=sprint_id)
    if not sprint.project.is_member(user):
        raise Http404("Sprint não encontrada.")
    return sprint


@login_required
def sprint_list_view(request, project_id):
    project = _get_project_or_404(project_id, request.user)

    qs = project.sprints.all().order_by("-start_date", "-created_at")

    paginator = Paginator(qs, 10)  # page size
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "sprints/sprint_list.html",
        {"project": project, "page_obj": page_obj},
    )


@login_required
def sprint_detail_view(request, sprint_id):
    sprint = _get_sprint_or_404(sprint_id, request.user)
    project = sprint.project

    can_manage = project.is_owner(request.user)

    return render(
        request,
        "sprints/sprint_detail.html",
        {"project": project, "sprint": sprint, "can_manage": can_manage},
    )


@login_required
def sprint_create_view(request, project_id):
    project = _get_project_or_404(project_id, request.user)

    if not project.is_owner(request.user):
        raise Http404("Você não tem permissão.")

    if request.method == "POST":
        form = SprintForm(request.POST)
        if form.is_valid():
            sprint = form.save(commit=False)
            sprint.project = project
            sprint.full_clean()
            sprint.save()
            return redirect("sprint_list", project_id=project.id)
    else:
        form = SprintForm()

    return render(
        request,
        "sprints/sprint_form.html",
        {"project": project, "form": form, "mode": "create", "title": "Nova Sprint", "button_text":"Criar"},
    )


@login_required
def sprint_update_view(request, sprint_id):
    sprint = _get_sprint_or_404(sprint_id, request.user)
    project = sprint.project

    if not project.is_owner(request.user):
        raise Http404("Você não tem permissão.")

    if request.method == "POST":
        form = SprintForm(request.POST, instance=sprint)
        if form.is_valid():
            sprint = form.save(commit=False)
            sprint.full_clean()
            sprint.save()
            return redirect("sprint_detail", sprint_id=sprint.id)
    else:
        form = SprintForm(instance=sprint)

    return render(
        request,
        "sprints/sprint_form.html",
        {"project": project, "form": form, "mode": "edit", "sprint": sprint, "title":"Editar Sprint", "button_text":"Editar" },
    )


@login_required
def sprint_close_view(request, sprint_id):
    sprint = _get_sprint_or_404(sprint_id, request.user)
    project = sprint.project

    if not project.is_owner(request.user):
        raise Http404("Você não tem permissão.")

    if request.method == "POST":
        sprint.status = Sprint.Status.CLOSED
        sprint.full_clean()
        sprint.save()
        return redirect("sprint_detail", sprint_id=sprint.id)

    return redirect("sprint_detail", sprint_id=sprint.id)

