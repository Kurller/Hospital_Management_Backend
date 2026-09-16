from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Department, Doctor, Patient, Appointment,DoctorAvailability


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Hospital Information", {
            "fields": ("role",),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Hospital Information", {
            "fields": ("role",),
        }),
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "department",
        "specialization",
        "license_number",
    )
    list_filter = ("department", "specialization")
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "license_number",
    )


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "gender",
        "blood_group",
    )
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
    )


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "patient",
        "doctor",
        "appointment_date",
        "appointment_time",
        "status",
    )
    list_filter = (
        "status",
        "appointment_date",
    )
    search_fields = (
        "patient__user__username",
        "doctor__user__username",
    )
@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "doctor",
        "day_of_week",
        "start_time",
        "end_time",
        "is_active",
    )

    list_filter = (
        "day_of_week",
        "is_active",
    )

    search_fields = (
        "doctor__user__username",
        "doctor__user__first_name",
        "doctor__user__last_name",
    )