from datetime import date, timedelta

from django.contrib.auth.models import Group, Permission, User
from django.test import TestCase
from django.urls import reverse

from scrum_app.models import Project, ProjectMember, Sprint


class SprintTests(TestCase):
    def setUp(self):
        self.member_group, _ = Group.objects.get_or_create(name="member")
        self.editor_group, _ = Group.objects.get_or_create(name="editor")

        # Permissões (sprint)
        perm_view = Permission.objects.get(codename="view_sprint")
        perm_add = Permission.objects.get(codename="add_sprint")
        perm_change = Permission.objects.get(codename="change_sprint")

        self.member_group.permissions.set([perm_view])
        self.editor_group.permissions.set([perm_view, perm_add, perm_change])

        self.editor = User.objects.create_user(username="editor", password="123")
        self.member = User.objects.create_user(username="member", password="123")
        self.outsider = User.objects.create_user(username="outsider", password="123")

        self.editor.groups.add(self.editor_group)
        self.member.groups.add(self.member_group)
        self.outsider.groups.add(self.member_group)  # tem view_sprint, mas não é membro do projeto

        self.project = Project.objects.create(name="Projeto", owner=self.editor)
        ProjectMember.objects.create(project=self.project, user=self.member)

        self.sprint = Sprint.objects.create(
            project=self.project,
            name="Sprint 1",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7),
            status=Sprint.Status.PLANNING,
        )

    def test_member_can_view_sprint_list_if_project_member(self):
        self.client.login(username="member", password="123")
        resp = self.client.get(reverse("sprint_list", kwargs={"project_id": self.project.id}))
        self.assertEqual(resp.status_code, 200)

    def test_outsider_cannot_view_sprint_list_even_with_view_perm(self):
        self.client.login(username="outsider", password="123")
        resp = self.client.get(reverse("sprint_list", kwargs={"project_id": self.project.id}))
        self.assertEqual(resp.status_code, 403)

    def test_editor_can_create_sprint(self):
        self.client.login(username="editor", password="123")
        url = reverse("sprint_create", kwargs={"project_id": self.project.id})
        payload = {
            "name": "Sprint 2",
            "description": "desc",
            "start_date": str(date.today()),
            "end_date": str(date.today() + timedelta(days=10)),
            "status": Sprint.Status.PLANNING,
        }
        resp = self.client.post(url, payload)

        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Sprint.objects.filter(project=self.project, name="Sprint 2").exists())

    def test_member_cannot_create_sprint(self):
        self.client.login(username="member", password="123")
        url = reverse("sprint_create", kwargs={"project_id": self.project.id})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 403)

    def test_member_can_view_sprint_detail_if_project_member(self):
        self.client.login(username="member", password="123")
        resp = self.client.get(reverse("sprint_detail", kwargs={"sprint_id": self.sprint.id}))
        self.assertEqual(resp.status_code, 200)