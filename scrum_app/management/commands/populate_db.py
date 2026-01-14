"""
Django management command to populate database with fake data for testing.
"""

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from faker import Faker

from scrum_app.models import Project, ProjectMember


class Command(BaseCommand):
    help = "Populate database with fake users and projects for testing"

    def add_arguments(self, parser):
        parser.add_argument(
            "--users",
            type=int,
            default=10,
            help="Number of users to create (default: 10)",
        )
        parser.add_argument(
            "--projects",
            type=int,
            default=5,
            help="Number of projects per user (default: 5)",
        )
        parser.add_argument(
            "--clear", action="store_true", help="Clear existing data before populating"
        )

    def handle(self, *args, **options):
        fake = Faker("pt_BR")
        num_users = options["users"]
        num_projects = options["projects"]

        if options["clear"]:
            self.stdout.write(self.style.WARNING("Clearing existing data..."))
            ProjectMember.objects.all().delete()
            Project.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS("Data cleared!"))

        # Create users
        self.stdout.write(f"Creating {num_users} fake users...")
        users = []
        for i in range(num_users):
            username = fake.user_name()
            # Ensure unique username
            while User.objects.filter(username=username).exists():
                username = fake.user_name()

            user = User.objects.create_user(
                username=username,
                email=fake.email(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                password="senha123",
            )
            users.append(user)
            self.stdout.write(f"  ✓ Created user: {user.username}")

        # Create projects
        self.stdout.write(f"\nCreating {num_projects} projects per user...")
        total_projects = 0
        for user in users:
            for _ in range(num_projects):
                project = Project.objects.create(
                    name=fake.catch_phrase(),
                    description=fake.text(max_nb_chars=200),
                    owner=user,
                )
                total_projects += 1

                # Add some random members to the project
                num_members = fake.random_int(min=0, max=min(3, len(users) - 1))
                available_users = [u for u in users if u != user]
                members = fake.random_elements(
                    elements=available_users, length=num_members, unique=True
                )

                for member in members:
                    ProjectMember.objects.create(project=project, user=member)

                self.stdout.write(
                    f'  ✓ Created project "{project.name}" for {user.username} '
                    f"with {num_members} member(s)"
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Successfully created {len(users)} users and {total_projects} projects!"
            )
        )
        self.stdout.write(
            self.style.SUCCESS("You can login with any username and password: senha123")
        )
