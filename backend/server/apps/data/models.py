from django.db import models
from apps.authentication.models import Customer, Staff
import datetime


class Class(models.Model):
    # Define the fields of the Class model
    created_by = models.ForeignKey(Staff, on_delete=models.PROTECT)
    class_name = models.CharField(max_length=100, blank=False)
    description = models.CharField(max_length=500, blank=False)
    start_datetime = models.DateTimeField(blank=False)
    deleted = models.BooleanField(default=False, blank=False)


class Booking(models.Model):
    # Define the fields of the Booking model
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    class_id = models.ForeignKey(Class, on_delete=models.PROTECT)
    booking_datetime = models.DateTimeField(blank=False)
    cancellation = models.BooleanField(default=False, blank=False)


class Membership(models.Model):
    DURATION_CHOICES = (
        (1, "1 Month"),
        (6, "6 Months"),
        (12, "12 Months"),
    )

    # Define the fields of the Membership model
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    start_date = models.DateField(blank=False)
    end_date = models.DateField(blank=False)
    duration = models.IntegerField(
        choices=DURATION_CHOICES, default=1
    )  # Default to 1 month

    def __str__(self):
        return f"{self.customer.user.username} - {self.get_duration_display()}"


class PurchaseHistory(models.Model):
    # Define the fields of the PurchaseHistory model
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    membership = models.ForeignKey(Membership, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=False)
    purchase_datetime = models.DateTimeField(blank=False)
