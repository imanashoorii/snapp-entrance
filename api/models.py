from datetime import datetime

from django.db import models

from api.enums import TripStatus


class Vendor(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Order(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    delivery_time = models.DateTimeField(default=datetime.now)
    created_at = models.DateTimeField(auto_now_add=True)
    assigned_employee = models.ForeignKey('Employee', null=True, blank=True, on_delete=models.SET_NULL)


class Trip(models.Model):
    TRIP_STATUS = [
        (TripStatus.ASSIGNED, 'Assigned'),
        (TripStatus.PICKED, 'Picked'),
        (TripStatus.VENDOR_AT, 'Vendor at'),
        (TripStatus.DELIVERED, 'Delivered'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    status = models.PositiveIntegerField(choices=TRIP_STATUS)


class ReportDelay(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    delay_time = models.IntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)


class Employee(models.Model):
    name = models.CharField(max_length=255)
    has_inspections = models.BooleanField(default=False)
