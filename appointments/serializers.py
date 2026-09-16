from rest_framework import serializers
from django.utils import timezone
from accounts.models import Appointment, DoctorAvailability


from rest_framework import serializers

from accounts.models import Appointment, DoctorAvailability


class AppointmentSerializer(serializers.ModelSerializer):

    patient_name = serializers.CharField(
        source="patient.user.get_full_name",
        read_only=True
    )

    doctor_name = serializers.CharField(
        source="doctor.user.get_full_name",
        read_only=True
    )

    doctor_specialization = serializers.CharField(
        source="doctor.specialization",
        read_only=True
    )

    class Meta:
        model = Appointment
        fields = [
            "id",
            "patient",
            "patient_name",
            "doctor",
            "doctor_name",
            "doctor_specialization",
            "appointment_date",
            "appointment_time",
            "reason",
            "status",
            "notes",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "patient",
            "patient_name",
            "doctor_name",
            "doctor_specialization",
            "status",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        doctor = attrs.get("doctor")
        appointment_date = attrs.get("appointment_date")
        appointment_time = attrs.get("appointment_time")

        today = timezone.localdate()
        now = timezone.localtime().time()

        if appointment_date < today:
            raise serializers.ValidationError(
                "You cannot book an appointment in the past."
            )

        if appointment_date == today and appointment_time <= now:
            raise serializers.ValidationError(
                "You cannot book an appointment at a time that has already passed."
            )

        day_of_week = appointment_date.weekday()

        availability_exists = DoctorAvailability.objects.filter(
            doctor=doctor,
            day_of_week=day_of_week,
            start_time__lte=appointment_time,
            end_time__gte=appointment_time,
            is_active=True,
        ).exists()

        if not availability_exists:
            raise serializers.ValidationError(
                "The doctor is not available at this time."
            )

        existing = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status__in=[
                Appointment.Status.SCHEDULED,
                Appointment.Status.CONFIRMED,
            ],
        )

        if self.instance:
            existing = existing.exclude(pk=self.instance.pk)

        if existing.exists():
            raise serializers.ValidationError(
                "This doctor already has an appointment at this time."
            )

        return attrs

class DoctorAvailabilitySerializer(serializers.ModelSerializer):

    class Meta:
        model = DoctorAvailability
        fields = [
            "id",
            "doctor",
            "day_of_week",
            "start_time",
            "end_time",
            "is_active",
        ]
        read_only_fields = ["doctor"]

