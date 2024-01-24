from django.contrib import admin
from api.models import ReportDelay, Vendor, Order, Trip, Employee

admin.site.register(ReportDelay)
admin.site.register(Vendor)
admin.site.register(Order)
admin.site.register(Trip)
admin.site.register(Employee)
