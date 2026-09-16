from rest_framework import generics
from django.db.models import Q
from rest_framework.permissions import AllowAny, IsAuthenticated
from accounts.models import Appointment,DoctorAvailability
from .serializers import AppointmentSerializer
from rest_framework.response import Response
from .permissions import IsDoctor,IsAdmin
from datetime import datetime
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,DoctorSerializer,StaffUserSerializer,DoctorCreateSerializer,AppointmentStatusSerializer,DoctorAvailabilitySerializer
)
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class AppointmentListCreateView(generics.ListCreateAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

    # -----------------------------
    # Get appointments user can see
    # -----------------------------

        if user.role == user.Role.PATIENT:
           queryset = Appointment.objects.filter(
            patient__user=user
        )

        elif user.role == user.Role.DOCTOR:
            queryset = Appointment.objects.filter(
            doctor__user=user
        )

        else:
            queryset = Appointment.objects.all()

    # -----------------------------
    # Filter by status
    # -----------------------------

        status = self.request.query_params.get("status")

        if status:
           valid_statuses = [
            choice[0]
            for choice in Appointment.Status.choices
        ]

        if status not in valid_statuses:
            from rest_framework.exceptions import ValidationError

            raise ValidationError({
                "status": "Invalid appointment status."
            })

        queryset = queryset.filter(
            status=status
        )

    # -----------------------------
    # Filter by date
    # -----------------------------

        appointment_date = self.request.query_params.get("date")

        if appointment_date:
            try:
                appointment_date = datetime.strptime(
            appointment_date,
            "%Y-%m-%d"
        ).date()

            except ValueError:
                  from rest_framework.exceptions import ValidationError

        raise ValidationError({
            "date": "Invalid date format. Use YYYY-MM-DD."
        })

        queryset = queryset.filter(
        appointment_date=appointment_date
    )
        from_date = self.request.query_params.get("from_date")
        to_date = self.request.query_params.get("to_date")

        if from_date:
           try:
              from_date = datetime.strptime(
            from_date,
            "%Y-%m-%d"
        ).date()
           except ValueError:
                 raise ValidationError({
            "from_date": "Invalid date format. Use YYYY-MM-DD."
        })

        queryset = queryset.filter(
        appointment_date__gte=from_date
    )

        if to_date:
            try:
              to_date = datetime.strptime(
            to_date,
            "%Y-%m-%d"
        ).date()
            except ValueError:
                 raise ValidationError({
            "to_date": "Invalid date format. Use YYYY-MM-DD."
        })

        queryset = queryset.filter(
        appointment_date__lte=to_date
    )
        # -----------------------------
# Search by patient name
# -----------------------------

        search = self.request.query_params.get("search")

        if search:
           queryset = queryset.filter(
        Q(patient__user__first_name__icontains=search)
        | Q(patient__user__last_name__icontains=search)
        | Q(patient__user__username__icontains=search)
        | Q(patient__phone__icontains=search)
        | Q(reason__icontains=search)
        | Q(doctor__user__first_name__icontains=search)
        | Q(doctor__user__last_name__icontains=search)
        | Q(doctor__user__username__icontains=search)
        | Q(doctor__specialization__icontains=search)
    )
    # -----------------------------
    # Order appointments
    # -----------------------------

        queryset = queryset.order_by(
        "appointment_date",
        "appointment_time"
    )

        return queryset
    def perform_create(self, serializer):
        patient = self.request.user.patient_profile

        serializer.save(
            patient=patient
        )
    


class DoctorProfileView(generics.RetrieveAPIView):
    serializer_class = DoctorSerializer
    permission_classes = [IsDoctor]

    def get_object(self):
        return self.request.user.doctor_profile



class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
class StaffUserCreateView(generics.CreateAPIView):
    serializer_class = StaffUserSerializer
    permission_classes = [IsAdmin]
class DoctorCreateView(generics.CreateAPIView):
    serializer_class = DoctorCreateSerializer
    permission_classes = [IsAdmin]
class AppointmentStatusUpdateView(generics.UpdateAPIView):
    serializer_class = AppointmentStatusSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == user.Role.PATIENT:
            return Appointment.objects.filter(
                patient__user=user
            )

        if user.role == user.Role.DOCTOR:
            return Appointment.objects.filter(
                doctor__user=user
            )

        return Appointment.objects.all()

    def update(self, request, *args, **kwargs):
        appointment = self.get_object()

        serializer = self.get_serializer(
            appointment,
            data=request.data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(serializer.data)
class DoctorAvailabilityListCreateView(generics.ListCreateAPIView):
    serializer_class = DoctorAvailabilitySerializer
    permission_classes = [IsDoctor]

    def get_queryset(self):
        return DoctorAvailability.objects.filter(
            doctor=self.request.user.doctor_profile
        )

    def perform_create(self, serializer):
        doctor = self.request.user.doctor_profile

        serializer.save(
            doctor=doctor
        )
