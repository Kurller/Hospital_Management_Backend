from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from accounts.models import Appointment,DoctorAvailability
from .serializers import AppointmentSerializer,DoctorAvailabilitySerializer
from .permissions import IsDoctor
from .pagination import AppointmentPagination
class DoctorAppointmentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        appointments = Appointment.objects.filter(
            doctor__user=request.user
        )

        serializer = AppointmentSerializer(appointments, many=True)

        return Response(serializer.data)
class AppointmentListCreateView(APIView):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = AppointmentPagination
    def post(self, request):
        serializer = AppointmentSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        patient = request.user.patient_profile

        serializer.save(patient=patient)

        return Response(
            serializer.data,
            status=201
        )
class DoctorAvailabilityDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DoctorAvailabilitySerializer
    permission_classes = [IsDoctor]

    def get_queryset(self):
        return DoctorAvailability.objects.filter(
            doctor=self.request.user.doctor_profile
        )