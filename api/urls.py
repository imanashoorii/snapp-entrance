from django.urls import path

from api.views import DelayOrderAPIView, AssignOrderToEmployeeAPIView, VendorDelayAPIView

urlpatterns = [
    path('delay/report/<int:order_id>/', DelayOrderAPIView.as_view(), name='report_delay'),
    path('delay/report/weekly', VendorDelayAPIView.as_view(), name='weekly_report'),
    path('delay/assign', AssignOrderToEmployeeAPIView.as_view(), name='assign_operator_to_delay'),
]
