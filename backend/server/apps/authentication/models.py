from django.db import models
from django.contrib.auth.models import AbstractUser


class fitopiaUser(AbstractUser):
    first_name = models.CharField(max_length=100, blank=False)
    last_name = models.CharField(max_length=100, blank=False)
    username = models.CharField(
        max_length=200, blank=False, unique=True
    )  # Username is email
    password = models.CharField(max_length=100, blank=False)
    email = models.EmailField(max_length=200, blank=False)
    is_active = models.BooleanField(default=True, blank=True)

    # Add related_name to avoid clashes
    groups = models.ManyToManyField(
        "auth.Group", related_name="fitopia_users_groups", blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission", related_name="fitopia_users_permissions", blank=True
    )

    def __str__(self):
        return self.username


class Administrator(models.Model):
    # Define the fields of the Administrator model
    user = models.ForeignKey(fitopiaUser, on_delete=models.PROTECT)

    def is_admin(user):
        return Administrator.objects.filter(user=user).exists()


class Customer(models.Model):
    # Define the fields of the Customer model
    user = models.ForeignKey(fitopiaUser, on_delete=models.PROTECT)
    password_reset = models.BooleanField(default=False, blank=False)

    def is_customer(user):
        return Customer.objects.filter(user=user).exists()


class Staff(models.Model):
    # Define the fields of the Staff model
    user = models.ForeignKey(fitopiaUser, on_delete=models.PROTECT)
    created_by = models.ForeignKey(Administrator, on_delete=models.PROTECT)
    password_reset = models.BooleanField(default=True, blank=False)

    def is_staff(user):
        return Staff.objects.filter(user=user).exists()

class Otp(models.Model):
    user = models.ForeignKey(fitopiaUser, on_delete=models.PROTECT, null=True)
    otp = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True)
    is_used = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    last_attempt_at = models.DateTimeField(null=True, blank=True)
