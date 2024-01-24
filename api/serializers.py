from rest_framework import serializers

from api.models import ReportDelay


class ReportDelaySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportDelay
        fields = '__all__'


class AssignEmployeeSerializer(serializers.Serializer):
    employee = serializers.IntegerField()


class VendorDelaySerializer(serializers.Serializer):
    vendor = serializers.CharField()
    delays = serializers.ListField(child=serializers.DictField())
