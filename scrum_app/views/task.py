"""Views for Task management and Kanban board."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from scrum_app.forms.task_forms import TaskCommentForm, TaskForm
from scrum_app.models import Task, TaskComment, UserStory


def _get_project_from_user_story(user_story):
    """Helper to get project from user story."""
    if user_story.product_backlog:
        return user_story.product_backlog.project
    return user_story.sprint_backlog.sprint.project


def _check_user_access(user, project):
    """Helper to check if user has access to project."""
    return project.is_member(user)


@login_required
def task_kanban_view(request, user_story_pk):
    """View to display Kanban board for a user story's tasks."""
    user_story = get_object_or_404(UserStory, pk=user_story_pk)
    project = _get_project_from_user_story(user_story)

    # Check if user is member or owner
    if not _check_user_access(request.user, project):
        messages.error(request, "Você não tem permissão para acessar esta user story.")
        return redirect("project_list")

    # Get tasks grouped by status
    tasks_todo = user_story.tasks.filter(status=Task.Status.TODO)
    tasks_in_progress = user_story.tasks.filter(status=Task.Status.IN_PROGRESS)
    tasks_done = user_story.tasks.filter(status=Task.Status.DONE)

    context = {
        "user_story": user_story,
        "project": project,
        "tasks_todo": tasks_todo,
        "tasks_in_progress": tasks_in_progress,
        "tasks_done": tasks_done,
    }

    return render(request, "tasks/task_kanban.html", context)


@login_required
def task_create_view(request, user_story_pk):
    """Create a new task for a user story."""
    user_story = get_object_or_404(UserStory, pk=user_story_pk)
    project = _get_project_from_user_story(user_story)

    # Check if user is member or owner
    if not _check_user_access(request.user, project):
        messages.error(request, "Você não tem permissão para acessar esta user story.")
        return redirect("project_list")

    if request.method == "POST":
        form = TaskForm(request.POST, project=project)
        if form.is_valid():
            task = form.save(commit=False)
            task.user_story = user_story
            task.save()
            messages.success(request, "Task criada com sucesso!")
            return redirect("task_kanban", user_story_pk=user_story.pk)
    else:
        form = TaskForm(project=project)

    context = {
        "form": form,
        "user_story": user_story,
        "project": project,
    }

    return render(request, "tasks/task_form.html", context)


@login_required
def task_update_view(request, pk):
    """Update an existing task."""
    task = get_object_or_404(Task, pk=pk)
    user_story = task.user_story
    project = _get_project_from_user_story(user_story)

    # Check if user is member or owner
    if not _check_user_access(request.user, project):
        messages.error(request, "Você não tem permissão para editar esta task.")
        return redirect("project_list")

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task, project=project)
        if form.is_valid():
            form.save()
            messages.success(request, "Task atualizada com sucesso!")
            return redirect("task_detail", pk=task.pk)
    else:
        form = TaskForm(instance=task, project=project)

    context = {
        "form": form,
        "task": task,
        "user_story": user_story,
        "project": project,
        "is_update": True,
    }

    return render(request, "tasks/task_form.html", context)


@login_required
def task_delete_view(request, pk):
    """Delete a task."""
    task = get_object_or_404(Task, pk=pk)
    user_story = task.user_story
    project = _get_project_from_user_story(user_story)

    # Check if user is member or owner
    if not _check_user_access(request.user, project):
        messages.error(request, "Você não tem permissão para excluir esta task.")
        return redirect("project_list")

    if request.method == "POST":
        user_story_pk = task.user_story.pk
        task.delete()
        messages.success(request, "Task excluída com sucesso!")
        return redirect("task_kanban", user_story_pk=user_story_pk)

    context = {
        "task": task,
        "user_story": user_story,
        "project": project,
    }

    return render(request, "tasks/task_confirm_delete.html", context)


@login_required
def task_detail_view(request, pk):
    """Display task details with comments."""
    task = get_object_or_404(Task, pk=pk)
    user_story = task.user_story
    project = _get_project_from_user_story(user_story)

    # Check if user is member or owner
    if not _check_user_access(request.user, project):
        messages.error(request, "Você não tem permissão para visualizar esta task.")
        return redirect("project_list")

    # Handle comment submission
    if request.method == "POST":
        comment_form = TaskCommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.task = task
            comment.author = request.user
            comment.save()
            messages.success(request, "Comentário adicionado com sucesso!")
            return redirect("task_detail", pk=task.pk)
    else:
        comment_form = TaskCommentForm()

    comments = task.comments.all()

    context = {
        "task": task,
        "user_story": user_story,
        "project": project,
        "comments": comments,
        "comment_form": comment_form,
    }

    return render(request, "tasks/task_detail.html", context)


@login_required
@require_POST
def task_update_status_view(request, pk):
    """AJAX view to update task status (for drag and drop in Kanban)."""
    task = get_object_or_404(Task, pk=pk)
    user_story = task.user_story
    project = _get_project_from_user_story(user_story)

    # Check if user is member or owner
    if not _check_user_access(request.user, project):
        return JsonResponse({"success": False, "error": "Acesso negado"}, status=403)

    new_status = request.POST.get("status")

    if new_status in dict(Task.Status.choices):
        task.status = new_status
        task.save()
        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "error": "Status inválido"}, status=400)


@login_required
@require_POST
def task_comment_delete_view(request, pk):
    """Delete a comment from a task."""
    comment = get_object_or_404(TaskComment, pk=pk)
    task = comment.task
    user_story = task.user_story
    project = _get_project_from_user_story(user_story)

    # Check if user is the author or project owner
    if request.user != comment.author and not project.is_owner(request.user):
        messages.error(request, "Você não tem permissão para excluir este comentário.")
        return redirect("task_detail", pk=task.pk)

    comment.delete()
    messages.success(request, "Comentário excluído com sucesso!")
    return redirect("task_detail", pk=task.pk)
