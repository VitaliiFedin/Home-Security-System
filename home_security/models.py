from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models


class User(AbstractUser):
    ADMIN = 1
    MANAGER = 2
    GUARD = 3

    ROLE_CHOICES = (
        (ADMIN, "Administrator"),
        (MANAGER, "Manager"),
        (GUARD, "Guard"),
    )
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, blank=True, null=True)

    def is_admin(self):
        return self.role == self.ADMIN

    def is_manager(self):
        return self.role == self.MANAGER

    def is_guard(self):
        return self.role == self.GUARD


class Building(models.Model):
    number = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    manager = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="managed_buildings"
    )

    def __str__(self) -> str:
        return f"Building with number  {self.number}"


class Entrance(models.Model):
    building = models.ForeignKey(
        Building, on_delete=models.CASCADE, related_name="entrances"
    )
    number = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    guard = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="guarded_entrances"
    )

    def __str__(self) -> str:
        return f"Entrance with number {self.number}"


class Apartment(models.Model):
    entrance = models.ForeignKey(
        Entrance, on_delete=models.CASCADE, related_name="apartments"
    )
    number = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    def __str__(self) -> str:
        return f"Apartment with number {self.number}"


class Event(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp}"
