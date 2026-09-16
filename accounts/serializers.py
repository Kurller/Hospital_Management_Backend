from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Doctor
from django.db import transaction
from .models import Appointment, Department, Doctor,DoctorAvailability
User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
        ]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email"),
            first_name=validated_data.get("first_name"),
            last_name=validated_data.get("last_name"),
            password=validated_data["password"],
            role=User.Role.PATIENT,
        )

        Patient.objects.create(
            user=user
        )

        return user


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
        ]
        read_only_fields = [
            "id",
            "role",
        ]
class DoctorCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        write_only=True
    )

    email = serializers.EmailField(
        write_only=True
    )

    first_name = serializers.CharField(
        write_only=True
    )

    last_name = serializers.CharField(
        write_only=True
    )

    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    user = UserSerializer(
        read_only=True
    )

    class Meta:
        model = Doctor
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "user",
            "department",
            "specialization",
            "license_number",
            "phone",
            "bio",
        ]

        read_only_fields = [
            "id",
            "user",
        ]
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
            "A user with this username already exists."
        )

        return value

    @transaction.atomic
    def create(self, validated_data):
        username = validated_data.pop("username")
        email = validated_data.pop("email")
        first_name = validated_data.pop("first_name")
        last_name = validated_data.pop("last_name")
        password = validated_data.pop("password")

        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            role=User.Role.DOCTOR,
        )

        doctor = Doctor.objects.create(
            user=user,
            **validated_data
        )

        return doctor

class AppointmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Appointment
        fields = [
            "id",
            "patient",
            "doctor",
            "appointment_date",
            "appointment_time",
            "reason",
            "status",
            "notes",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "patient",
            "status",
            "created_at",
            "updated_at",
        ]

        def validate(self, attrs):
            doctor = attrs.get("doctor")
            appointment_date = attrs.get("appointment_date")
            appointment_time = attrs.get("appointment_time")

            if Appointment.objects.filter(
               doctor=doctor,
               appointment_date=appointment_date,
               appointment_time=appointment_time,
            ).exclude(
                 status__in=[
                    Appointment.Status.CANCELLED,
                    Appointment.Status.NO_SHOW,
                 ]
            ).exists():
                raise serializers.ValidationError(
            "This doctor is already booked for this date and time."
              )
            day_of_week = appointment_date.weekday()

            available = doctor.availabilities.filter(
        day_of_week=day_of_week,
        is_active=True,
        start_time__lte=appointment_time,
        end_time__gt=appointment_time,
    ).exists()
            if not available:
               raise serializers.ValidationError(
            "The doctor is not available at this date and time."
                )

            return attrs


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = [
            "id",
            "user",
            "department",
            "specialization",
            "license_number",
            "phone",
            "bio",
        ]
        read_only_fields = [
            "id",
            "user",
        ]
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
            "A user with this username already exists."
        )

        return value
    def validate_license_number(self, value):
        if Doctor.objects.filter(
        license_number=value
    ).exists():
            raise serializers.ValidationError(
            "A doctor with this license number already exists."
        )

        return value
class StaffUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "role",
        ]

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email"),
            first_name=validated_data.get("first_name"),
            last_name=validated_data.get("last_name"),
            password=validated_data["password"],
            role=validated_data["role"],
        )
class AppointmentStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = Appointment
        fields = ["status"]

    def validate_status(self, value):

        appointment = self.instance
        current_status = appointment.status
        user = self.context["request"].user

        # --------------------------------
        # Patient rules
        # --------------------------------

        if user.role == user.Role.PATIENT:

            # Patient can only cancel
            if value != Appointment.Status.CANCELLED:
                raise serializers.ValidationError(
                    "Patients can only cancel appointments."
                )

            # Patient can only cancel their own appointment
            if appointment.patient.user != user:
                raise serializers.ValidationError(
                    "You can only cancel your own appointment."
                )

        # --------------------------------
        # Doctor rules
        # --------------------------------

        elif user.role == user.Role.DOCTOR:

            # Doctor must own the appointment
            if appointment.doctor.user != user:
                raise serializers.ValidationError(
                    "You can only manage your own appointments."
                )

        # --------------------------------
        # Admin rules
        # --------------------------------

        elif user.role == user.Role.ADMIN:
            pass

        # --------------------------------
        # Other roles
        # --------------------------------

        else:
            raise serializers.ValidationError(
                "You are not allowed to change appointment status."
            )

        # --------------------------------
        # Status transition rules
        # --------------------------------

        allowed_transitions = {
            Appointment.Status.SCHEDULED: [
                Appointment.Status.CONFIRMED,
                Appointment.Status.CANCELLED,
            ],

            Appointment.Status.CONFIRMED: [
                Appointment.Status.COMPLETED,
                Appointment.Status.CANCELLED,
                Appointment.Status.NO_SHOW,
            ],

            Appointment.Status.COMPLETED: [],

            Appointment.Status.CANCELLED: [],

            Appointment.Status.NO_SHOW: [],
        }

        allowed = allowed_transitions.get(
            current_status,
            []
        )

        if value not in allowed:
            raise serializers.ValidationError(
                f"Cannot change appointment from "
                f"{current_status} to {value}."
            )

        return value
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