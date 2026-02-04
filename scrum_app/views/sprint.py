from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from ..forms.sprint_forms import SprintForm
from ..models import Project, Sprint


# Helpers

def _get_project_or_404(project_id, user):
    project = get_object_or_404(Project, id=project_id)
    if not project.is_member(user):
        raise PermissionDenied
    return project


def _get_sprint_or_404(sprint_id, user):
    sprint = get_object_or_404(Sprint, id=sprint_id)
    if not sprint.project.is_member(user):
        raise PermissionDenied
    return sprint


def _require_project_editor(project: Project, user) -> None:
    """Allow management within a project.

    Allowed:
    - superuser
    - project owner
    - user in global group 'editor'
    NOTE: must be project member (owner counts as member in your model)
    """
    if user.is_superuser:
        return

    if not project.is_member(user):
        raise PermissionDenied

    if project.is_owner(user):
        return

    if user.groups.filter(name="editor").exists():
        return

    raise PermissionDenied


def _can_manage_sprint(project: Project, user) -> bool:
    """Used for UI (show/hide buttons)."""
    return (
        user.is_superuser
        or project.is_owner(user)
        or user.groups.filter(name="editor").exists()
    )


# Sprint views

@login_required
@permission_required("scrum_app.view_sprint", raise_exception=True)
def sprint_list_view(request, project_id):
    project = _get_project_or_404(project_id, request.user)

    qs = project.sprints.all().order_by("-start_date", "-created_at")
    paginator = Paginator(qs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    can_manage = _can_manage_sprint(project, request.user)

    return render(
        request,
        "sprints/sprint_list.html",
        {"project": project, "page_obj": page_obj, "can_manage": can_manage},
    )


@login_required
@permission_required("scrum_app.view_sprint", raise_exception=True)
def sprint_detail_view(request, sprint_id):
    sprint = _get_sprint_or_404(sprint_id, request.user)
    project = sprint.project

    can_manage = _can_manage_sprint(project, request.user)

    return render(
        request,
        "sprints/sprint_detail.html",
        {"project": project, "sprint": sprint, "can_manage": can_manage},
    )


@login_required
@permission_required("scrum_app.add_sprint", raise_exception=True)
def sprint_create_view(request, project_id):
    project = _get_project_or_404(project_id, request.user)
    _require_project_editor(project, request.user)

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
        {
            "project": project,
            "form": form,
            "mode": "create",
            "title": "Nova Sprint",
            "button_text": "Criar",
        },
    )


@login_required
@permission_required("scrum_app.change_sprint", raise_exception=True)
def sprint_update_view(request, sprint_id):
    sprint = _get_sprint_or_404(sprint_id, request.user)
    project = sprint.project
    _require_project_editor(project, request.user)

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
        {
            "project": project,
            "form": form,
            "mode": "edit",
            "sprint": sprint,
            "title": "Editar Sprint",
            "button_text": "Editar",
        },
    )


@login_required
@permission_required("scrum_app.change_sprint", raise_exception=True)
def sprint_close_view(request, sprint_id):
    sprint = _get_sprint_or_404(sprint_id, request.user)
    project = sprint.project
    _require_project_editor(project, request.user)

    if request.method == "POST":
        sprint.status = Sprint.Status.CLOSED
        sprint.full_clean()
        sprint.save()

    return redirect("sprint_detail", sprint_id=sprint.id)