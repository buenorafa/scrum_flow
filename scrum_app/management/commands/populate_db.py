"""
Django management command to populate database with fake data for testing.
"""

from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from scrum_app.models import (
    ProductBacklog,
    Project,
    ProjectMember,
    Sprint,
    SprintBacklog,
    Task,
    TaskComment,
    UserStory,
)


# pylint: disable=no-member, missing-class-docstring
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
            "--sprints",
            type=int,
            default=3,
            help="Maximum number of sprints per project (default: 3)",
        )
        parser.add_argument(
            "--stories",
            type=int,
            default=5,
            help="Maximum number of user stories per backlog (default: 5)",
        )
        parser.add_argument(
            "--clear", action="store_true", help="Clear existing data before populating"
        )

    def handle(self, *args, **options):
        fake = Faker("pt_BR")
        num_users = options["users"]
        num_projects = options["projects"]
        max_sprints = options["sprints"]
        max_stories = options["stories"]

        if options["clear"]:
            self.stdout.write(self.style.WARNING("Clearing existing data..."))
            TaskComment.objects.all().delete()
            Task.objects.all().delete()
            UserStory.objects.all().delete()
            SprintBacklog.objects.all().delete()
            ProductBacklog.objects.all().delete()
            Sprint.objects.all().delete()
            ProjectMember.objects.all().delete()
            Project.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS("Data cleared!"))

        # Create users
        self.stdout.write(f"Creating {num_users} fake users...")
        users = []
        for _ in range(num_users):
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
        projects_list = []
        for user in users:
            for _ in range(num_projects):
                project = Project.objects.create(
                    name=fake.catch_phrase(),
                    description=fake.text(max_nb_chars=200),
                    owner=user,
                )
                total_projects += 1
                projects_list.append(project)

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

        # Create sprints for some projects
        self.stdout.write("\nCreating sprints for projects...")
        total_sprints = 0

        for project in projects_list:
            # Create sprints for 60% of projects randomly
            if fake.boolean(chance_of_getting_true=60):
                num_sprints = fake.random_int(min=1, max=max_sprints)

                for i in range(num_sprints):
                    # Generate dates for sprints
                    # Past sprints for closed/active, future for planning
                    days_offset = -30 * (
                        num_sprints - i - 1
                    )  # Older sprints further in the past
                    start_date = timezone.now().date() + timedelta(days=days_offset)
                    end_date = start_date + timedelta(
                        days=fake.random_int(min=7, max=21)
                    )

                    # Determine status based on dates
                    today = timezone.now().date()
                    if end_date < today:
                        status = Sprint.Status.CLOSED
                    elif start_date <= today <= end_date:
                        status = Sprint.Status.ACTIVE
                    else:
                        status = Sprint.Status.PLANNING

                    # Ensure only one active sprint per project
                    if status == Sprint.Status.ACTIVE:
                        if Sprint.objects.filter(
                            project=project, status=Sprint.Status.ACTIVE
                        ).exists():
                            status = Sprint.Status.PLANNING

                    Sprint.objects.create(
                        project=project,
                        name=f"Sprint {i + 1}",
                        description=fake.sentence(nb_words=10),
                        start_date=start_date,
                        end_date=end_date,
                        status=status,
                    )
                    total_sprints += 1

                self.stdout.write(
                    f'  ✓ Created {num_sprints} sprint(s) for project "{project.name}"'
                )

        # Create user stories for product backlogs and sprint backlogs
        self.stdout.write("\nCreating user stories for backlogs...")
        total_stories = 0

        user_story_titles = [
            "Login de usuário",
            "Cadastro de novo usuário",
            "Recuperação de senha",
            "Atualização de perfil",
            "Upload de avatar",
            "Busca avançada",
            "Filtros personalizados",
            "Exportação de dados",
            "Notificações por email",
            "Dashboard interativo",
            "Relatórios gerenciais",
            "Integração com API",
            "Sistema de comentários",
            "Avaliação por estrelas",
            "Compartilhamento social",
        ]

        priorities = [choice[0] for choice in UserStory.Priority.choices]
        statuses = [choice[0] for choice in UserStory.Status.choices]

        for project in projects_list:
            # Create product backlog and user stories
            product_backlog, _ = ProductBacklog.objects.get_or_create(project=project)
            num_product_stories = fake.random_int(min=2, max=max_stories)

            for _ in range(num_product_stories):
                title = fake.random_element(elements=user_story_titles)
                UserStory.objects.create(
                    title=f"{title} - {fake.word()}",
                    description=fake.text(max_nb_chars=200),
                    as_a=f"Como {fake.job()}",
                    i_want=f"Eu quero {fake.sentence(nb_words=5)}",
                    so_that=f"Para que eu possa {fake.sentence(nb_words=6)}",
                    acceptance_criteria=fake.text(max_nb_chars=150),
                    story_points=fake.random_element(elements=[1, 2, 3, 5, 8, 13]),
                    priority=fake.random_element(elements=priorities),
                    status=fake.random_element(elements=statuses),
                    product_backlog=product_backlog,
                )
                total_stories += 1

            # pylint: disable=line-too-long
            self.stdout.write(
                f'  ✓ Created {num_product_stories} user stories for product backlog of "{project.name}"'
            )

            # Create user stories for sprint backlogs
            sprints = project.sprints.all()
            for sprint in sprints:
                sprint_backlog, _ = SprintBacklog.objects.get_or_create(sprint=sprint)
                num_sprint_stories = fake.random_int(min=1, max=max_stories)

                for _ in range(num_sprint_stories):
                    title = fake.random_element(elements=user_story_titles)
                    UserStory.objects.create(
                        title=f"{title} - {fake.word()}",
                        description=fake.text(max_nb_chars=200),
                        as_a=f"Como {fake.job()}",
                        i_want=f"Eu quero {fake.sentence(nb_words=5)}",
                        so_that=f"Para que eu possa {fake.sentence(nb_words=6)}",
                        acceptance_criteria=fake.text(max_nb_chars=150),
                        story_points=fake.random_element(elements=[1, 2, 3, 5, 8, 13]),
                        priority=fake.random_element(elements=priorities),
                        status=fake.random_element(elements=statuses),
                        sprint_backlog=sprint_backlog,
                    )
                    total_stories += 1

                # pylint: disable=line-too-long
                self.stdout.write(
                    f'  ✓ Created {num_sprint_stories} user stories for sprint backlog of "{sprint.name}"'
                )

        # Create tasks for user stories
        self.stdout.write("\nCreating tasks for user stories...")
        total_tasks = 0
        total_comments = 0

        task_titles = [
            "Criar interface",
            "Implementar lógica",
            "Escrever testes",
            "Documentar código",
            "Revisar código",
            "Corrigir bugs",
            "Otimizar performance",
            "Adicionar validações",
            "Configurar ambiente",
            "Deploy em produção",
        ]

        task_priorities = [choice[0] for choice in Task.Priority.choices]
        task_statuses = [choice[0] for choice in Task.Status.choices]

        all_user_stories = UserStory.objects.all()

        for user_story in all_user_stories:
            # Get project to assign tasks to members
            if user_story.product_backlog:
                project = user_story.product_backlog.project
            else:
                project = user_story.sprint_backlog.sprint.project

            # Get project members
            member_ids = list(project.members.values_list("user_id", flat=True)) + [
                project.owner.id
            ]
            project_members = User.objects.filter(id__in=member_ids)

            # Create 2-5 tasks per user story
            num_tasks = fake.random_int(min=2, max=5)

            for _ in range(num_tasks):
                task = Task.objects.create(
                    user_story=user_story,
                    title=fake.random_element(elements=task_titles),
                    description=fake.text(max_nb_chars=150),
                    assigned_to=(
                        fake.random_element(elements=list(project_members))
                        if fake.boolean(chance_of_getting_true=70)
                        else None
                    ),
                    status=fake.random_element(elements=task_statuses),
                    priority=fake.random_element(elements=task_priorities),
                    estimated_hours=(
                        fake.random_element(elements=[0.5, 1, 2, 3, 4, 5, 8])
                        if fake.boolean(chance_of_getting_true=80)
                        else None
                    ),
                )
                total_tasks += 1

                # Add 0-3 comments to each task
                num_comments = fake.random_int(min=0, max=3)
                for _ in range(num_comments):
                    TaskComment.objects.create(
                        task=task,
                        author=fake.random_element(elements=list(project_members)),
                        content=fake.text(max_nb_chars=100),
                    )
                    total_comments += 1

        self.stdout.write(
            f"  ✓ Created {total_tasks} tasks with {total_comments} comments"
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Successfully created {len(users)} users, {total_projects} projects, "
                f"{total_sprints} sprints, {total_stories} user stories, "
                f"{total_tasks} tasks, and {total_comments} comments!"
            )
        )
        self.stdout.write(
            self.style.SUCCESS("You can login with any username and password: senha123")
        )
