from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        DOCTOR = "DOCTOR", "Doctor"
        PATIENT = "PATIENT", "Patient"
        RECEPTIONIST = "RECEPTIONIST", "Receptionist"
        PHARMACIST = "PHARMACIST", "Pharmacist"
        LAB_TECHNICIAN = "LAB_TECHNICIAN", "Lab Technician"
        ACCOUNTANT = "ACCOUNTANT", "Accountant"

    role = models.CharField(
    max_length=30,
    choices=Role.choices,
    default=Role.PATIENT,
)

    def __str__(self):
        return self.username
class Department(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True
    )
    description = models.TextField(
        blank=True
    )

    def __str__(self):
        return self.name
class Doctor(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="doctor_profile"
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="doctors"
    )

    specialization = models.CharField(
        max_length=100
    )

    license_number = models.CharField(
        max_length=100,
        unique=True
    )

    phone = models.CharField(
        max_length=20,
        blank=True
    )

    bio = models.TextField(
        blank=True
    )

    def __str__(self):
        return f"Dr. {self.user.get_full_name()}"
class Patient(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="patient_profile"
    )

    date_of_birth = models.DateField(
        null=True,
        blank=True
    )

    gender = models.CharField(
        max_length=20,
        choices=[
            ("MALE", "Male"),
            ("FEMALE", "Female"),
            ("OTHER", "Other"),
        ],
        blank=True
    )

    phone = models.CharField(
        max_length=20,
        blank=True
    )

    address = models.TextField(
        blank=True
    )

    emergency_contact_name = models.CharField(
        max_length=100,
        blank=True
    )

    emergency_contact_phone = models.CharField(
        max_length=20,
        blank=True
    )

    blood_group = models.CharField(
        max_length=5,
        blank=True
    )

    def __str__(self):
        return self.user.get_full_name()
class Appointment(models.Model):

    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED", "Scheduled"
        CONFIRMED = "CONFIRMED", "Confirmed"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"
        NO_SHOW = "NO_SHOW", "No Show"

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="appointments"
    )

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="appointments"
    )

    appointment_date = models.DateField()
    appointment_time = models.TimeField()

    reason = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
        models.UniqueConstraint(
            fields=[
                "doctor",
                "appointment_date",
                "appointment_time",
            ],
            condition=Q(
                status__in=[
                    "SCHEDULED",
                    "CONFIRMED",
                ]
            ),
            name="unique_active_doctor_appointment_slot",
        )
    ]

    def __str__(self):
        return (
            f"{self.patient.user.get_full_name()} - "
            f"Dr. {self.doctor.user.get_full_name()} - "
            f"{self.appointment_date}"
        )
class DoctorAvailability(models.Model):

    class DayOfWeek(models.IntegerChoices):
        MONDAY = 0, "Monday"
        TUESDAY = 1, "Tuesday"
        WEDNESDAY = 2, "Wednesday"
        THURSDAY = 3, "Thursday"
        FRIDAY = 4, "Friday"
        SATURDAY = 5, "Saturday"
        SUNDAY = 6, "Sunday"

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="availabilities"
    )

    day_of_week = models.IntegerField(
        choices=DayOfWeek.choices
    )

    start_time = models.TimeField()
    end_time = models.TimeField()

    is_active = models.BooleanField(
        default=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "doctor",
                    "day_of_week",
                    "start_time",
                    "end_time",
                ],
                name="unique_doctor_availability"
            )
        ]

    def __str__(self):
        return (
            f"Dr. {self.doctor.user.get_full_name()} - "
            f"{self.get_day_of_week_display()} "
            f"{self.start_time} - {self.end_time}"
        )