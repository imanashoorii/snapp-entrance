from datetime import datetime, timedelta

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.enums import TripStatus
from api.models import Order, ReportDelay, Employee, Trip
from api.models import Vendor


class DelayOrderAPIViewTestCase(TestCase):
    def setUp(self):
        self.vendor = Vendor.objects.create(name='Vendor1')
        self.order = Order.objects.create(vendor=self.vendor, delivery_time=datetime.now())
        self.trip = Trip.objects.create(order=self.order, status=TripStatus.ASSIGNED)
        self.url = reverse('report_delay', args=[self.order.id])

    def test_delay_order_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('تاخیر با موفقیت ثبت شد.', response.data['message'])

    def test_delay_order_invalid_order_id(self):
        invalid_url = reverse('report_delay', args=[999])
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('سفارش یافت نشد.', response.data['message'])

    def test_delay_order_order_not_found(self):
        non_existent_order_id = self.order.id + 1
        non_existent_url = reverse('report_delay', args=[non_existent_order_id])
        response = self.client.get(non_existent_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('سفارش یافت نشد.', response.data['message'])


class AssignOrderToEmployeeAPIViewTestCase(APITestCase):
    def setUp(self):
        self.vendor = Vendor.objects.create(name='Vendor1')
        self.order = Order.objects.create(vendor=self.vendor, delivery_time=datetime.now())
        self.employee = Employee.objects.create(name='Test Operator', has_inspections=False)
        self.url = reverse('assign_operator_to_delay')
        self.delay_report = ReportDelay.objects.create(order=self.order)

    def test_assign_order_to_employee_success(self):
        data = {'employee': self.employee.id}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('درخواست تاخیر با موفقیت به اوپراتور تخصیص داده شد.', response.data['message'])

    def test_assign_order_to_employee_invalid_employee_id(self):
        invalid_data = {'employee': 999}
        response = self.client.post(self.url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('اوپراتور یافت نشد.', response.data['message'])

    def test_assign_order_to_employee_order_already_assigned(self):
        self.delay_report.order.assigned_employee = self.employee
        self.delay_report.order.save()
        data = {'employee': self.employee.id}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('سفارش درحال پیگیری است.', response.data['message'])


class VendorDelayAPIViewTestCase(APITestCase):
    def setUp(self):
        self.vendor1 = Vendor.objects.create(name='Vendor1')
        self.vendor2 = Vendor.objects.create(name='Vendor2')
        self.order1 = Order.objects.create(vendor=self.vendor1, delivery_time=datetime.now() - timedelta(days=5))
        self.order2 = Order.objects.create(vendor=self.vendor2, delivery_time=datetime.now() - timedelta(days=3))
        self.delay_report1 = ReportDelay.objects.create(order=self.order1, delay_time=10)
        self.delay_report2 = ReportDelay.objects.create(order=self.order2, delay_time=15)
        self.url = reverse('weekly_report')

    def test_vendor_delay_api_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertIn('Vendor1', [item['vendor'] for item in response.data])
        self.assertIn('Vendor2', [item['vendor'] for item in response.data])

