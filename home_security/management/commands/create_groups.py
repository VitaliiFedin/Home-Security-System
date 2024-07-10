from typing import Any

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from home_security.models import Apartment, Building, Entrance, User


class Command(BaseCommand):
    help = "Creates user groups and sets permissions"

    def handle(self, *args: Any, **options: Any) -> str | None:
        admin_group, _ = Group.objects.get_or_create(name="Administrator")
        manager_group, _ = Group.objects.get_or_create(name="Building Manager")
        guard_group, _ = Group.objects.get_or_create(name="Guard")

        building_content_type = ContentType.objects.get_for_model(Building)
        entrance_content_type = ContentType.objects.get_for_model(Entrance)
        apartment_content_type = ContentType.objects.get_for_model(Apartment)
        user_content_type = ContentType.objects.get_for_model(User)

        assign_guard_permission, created = Permission.objects.get_or_create(
            codename="assign_guard",
            name="Can assign guard to entrance",
            content_type=entrance_content_type,
        )

        admin_permissions = Permission.objects.filter(
            content_type__in=[
                building_content_type,
                entrance_content_type,
                apartment_content_type,
                user_content_type,
            ]
        )
        admin_permissions |= Permission.objects.filter(codename="assign_guard")
        admin_group.permissions.set(admin_permissions)

        manager_permissions = Permission.objects.filter(
            content_type__in=[building_content_type, entrance_content_type],
            codename__in=[
                "add_building",
                "change_building",
                "view_building",
                "delete_building",
                "add_entrance",
                "change_entrance",
                "view_entrance",
                "delete_entrance",
                "manage_building",
                "assign_guard",
            ],
        )
        manager_group.permissions.set(manager_permissions)

        guard_permissions = Permission.objects.filter(
            content_type=entrance_content_type,
            codename__in=["view_entrance", "guard_entrance"],
        )
        guard_permissions |= Permission.objects.filter(
            content_type=apartment_content_type, codename="view_apartment"
        )
        guard_group.permissions.set(guard_permissions)

        self.stdout.write(
            self.style.SUCCESS("Successfully created groups and set permissions")
        )

        # Додаємо користувачів до відповідних груп
        for user in User.objects.all():
            if user.is_admin():
                admin_group.user_set.add(user)
            elif user.is_manager():
                manager_group.user_set.add(user)
            elif user.is_guard():
                guard_group.user_set.add(user)

        self.stdout.write(self.style.SUCCESS("Successfully added users to groups"))
