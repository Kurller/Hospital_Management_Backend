from django.urls import path

from .views import (
    RegisterView,
    MeView,
    AppointmentListCreateView,DoctorProfileView,UserListView,StaffUserCreateView,DoctorCreateView,AppointmentStatusUpdateView,DoctorAvailabilityListCreateView
          )


urlpatterns = [
    path(
        "register/",
        RegisterView.as_view(),
        name="register",
    ),

    path(
        "me/",
        MeView.as_view(),
        name="me",
    ),

    path(
        "appointments/",
        AppointmentListCreateView.as_view(),
        name="appointment-list-create",
    ),
    



    path(
        "doctor/profile/",
        DoctorProfileView.as_view(),
        name="doctor-profile",
    ),
    path(
    "users/",
    UserListView.as_view(),
    name="user-list",
),
path(
    "staff/",
    StaffUserCreateView.as_view(),
    name="staff-create",
),
path(
    "admin/doctors/",
    DoctorCreateView.as_view(),
    name="admin-doctor-create",
),
path(
    "appointments/<int:pk>/status/",
    AppointmentStatusUpdateView.as_view(),
    name="appointment-status-update",
),
path(
    "doctor/availability/",
    DoctorAvailabilityListCreateView.as_view(),
    name="doctor-availability",
),


]
