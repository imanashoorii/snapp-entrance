from datetime import timedelta, datetime

from django.db.models import Min

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from .enums import TripStatus
from .models import Order, Trip, ReportDelay, Employee
from .serializers import ReportDelaySerializer, AssignEmployeeSerializer, VendorDelaySerializer


class DelayOrderAPIView(generics.GenericAPIView):
    serializer_class = ReportDelaySerializer

    def get(self, request, order_id):
        try:
            order = Order.objects.get(pk=order_id)

            try:
                trip = Trip.objects.get(order=order)
                if trip.status in [TripStatus.ASSIGNED, TripStatus.VENDOR_AT, TripStatus.PICKED]:
                    existing_delay_report = ReportDelay.objects.filter(order=order).first()
                    if not existing_delay_report and order.delivery_time < datetime.now():
                        '''
                        Send request to external service to get new estimated delay.
                        Note: https://run.mocky.io/v3/122c2796-5df4-461c-ab75-87c1192b17f7 <- this api mocker is
                        not working so I mock it manually.
                        '''
                        response = {"estimated_delivery_time": 15}
                        estimated_delivery_time = response.get('estimated_delivery_time')

                        order.delivery_time = order.delivery_time + timedelta(minutes=estimated_delivery_time)
                        order.save()

                        report = ReportDelay(order=order, delay_time=estimated_delivery_time)
                        report.save()

                        return Response(
                            {'message': 'تاخیر با موفقیت ثبت شد.'},
                            status=status.HTTP_200_OK
                        )
                    else:
                        return Response({'message': 'سفارش در صف تاخیر قراردارد یا هنوز زمان سفارش کامل نشده است'},
                                        status=status.HTTP_400_BAD_REQUEST)
            except Trip.DoesNotExist:
                report = ReportDelay(order=order)
                report.save()
                return Response(
                    {'message': 'سفارش در صف تاخیر قرار گرفت.'},
                    status=status.HTTP_200_OK
                )

        except Order.DoesNotExist:
            return Response(
                {'message': 'سفارش یافت نشد.'},
                status=status.HTTP_404_NOT_FOUND
            )


class AssignOrderToEmployeeAPIView(generics.GenericAPIView):
    serializer_class = AssignEmployeeSerializer

    def post(self, request):
        try:
            serializer = AssignEmployeeSerializer(data=request.data)
            if serializer.is_valid():
                employee_id = serializer.validated_data['employee']

                earliest_delay_report = ReportDelay.objects.all().aggregate(Min('created_at'))
                if earliest_delay_report:
                    earliest_report_time = earliest_delay_report['created_at__min']
                    delay_report_to_assign = ReportDelay.objects.filter(created_at=earliest_report_time).first()

                    if not delay_report_to_assign.order.assigned_employee:
                        employee_to_assign = Employee.objects.get(pk=employee_id)
                        employee_to_assign.has_inspections = True
                        employee_to_assign.save()

                        delay_report_to_assign.order.assigned_employee = employee_to_assign
                        delay_report_to_assign.order.save()

                        return Response({'message': 'درخواست تاخیر با موفقیت به اوپراتور تخصیص داده شد.'},
                                        status=status.HTTP_200_OK)
                    elif delay_report_to_assign.order.assigned_employee and delay_report_to_assign.order.assigned_employee.has_inspections:
                        return Response({'message': 'این اوپراتور درخواستی سفارش درحال پیگیری دارد.'},
                                        status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({'message': 'سفارش درحال پیگیری است.'},
                                        status=status.HTTP_400_BAD_REQUEST)

                else:
                    return Response({'message': 'سفارشی در لیست تاخیر موجود نیست'}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Employee.DoesNotExist:
            return Response({'message': 'اوپراتور یافت نشد.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VendorDelayAPIView(generics.ListAPIView):
    serializer_class = VendorDelaySerializer

    def get_queryset(self):
        now = datetime.now()
        start_of_week = now - timedelta(days=7)

        vendor_delays = ReportDelay.objects.filter(
            order__vendor__isnull=False,
            created_at__gte=start_of_week,
        ).values('order__vendor__name', 'delay_time', 'created_at').order_by('order__vendor__name', '-created_at')

        grouped_delays = {}
        for item in vendor_delays:
            vendor_name = item['order__vendor__name']
            delay_info = {'delay_time': item['delay_time'], 'created_at': item['created_at']}

            if vendor_name not in grouped_delays:
                grouped_delays[vendor_name] = [delay_info]
            else:
                grouped_delays[vendor_name].append(delay_info)

        return [
            {'vendor': vendor_name, 'delays': delays_info}
            for vendor_name, delays_info in grouped_delays.items()
        ]
