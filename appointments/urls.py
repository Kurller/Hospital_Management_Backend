from django.urls import path

from .views import DoctorAppointmentListView


urlpatterns = [
    path(
        "doctor/",
        DoctorAppointmentListView.as_view(),
        name="doctor-appointments",
    ),
]