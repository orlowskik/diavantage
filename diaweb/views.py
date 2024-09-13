from django.core.serializers import serialize
from django.shortcuts import render
from django.contrib.auth.models import User
from django.views.generic import TemplateView
from rest_framework import viewsets
from rest_framework.decorators import action, api_view, renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView

from diaweb.models import Patient, Physician, Address, Glucose, Blood, Appointment, Reception
from diaweb.serializers import PatientSerializer, PhysicianSerializer, AddressSerializer, \
    GlucoseSerializer, BloodSerializer, AppointmentSerializer, ReceptionSerializer


# Create your views here
class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer


class PatientRegistrationView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'diaweb/registration.html'
    style = {'template_pack': 'rest_framework/vertical'}
    serializer = PatientSerializer
    hidden_fields = ['id', 'confirmed_diabetes', 'classifier_result', 'last_appointment']

    def get(self, request):
        return Response({'serializer': self.serializer, 'style': self.style,
                         'hidden_fields': self.hidden_fields, 'name': 'Patient',
                         'target': 'patient-list'},
                        )


class PhysicianViewSet(viewsets.ModelViewSet):
    queryset = Physician.objects.all()
    serializer_class = PhysicianSerializer


class PhysicianRegistrationView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'diaweb/registration.html'
    style = {'template_pack': 'rest_framework/vertical'}
    serializer = PhysicianSerializer
    hidden_fields = ['id']

    def get(self, request):
        return Response({'serializer': self.serializer, 'style': self.style,
                         'hidden_fields': self.hidden_fields, 'name': 'Physician',
                         'target': 'physician-list'},
                        )


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer


class GlucoseViewSet(viewsets.ModelViewSet):
    queryset = Glucose.objects.all()
    serializer_class = GlucoseSerializer


class BloodViewSet(viewsets.ModelViewSet):
    queryset = Blood.objects.all()
    serializer_class = BloodSerializer


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer


class ReceptionViewSet(viewsets.ModelViewSet):
    queryset = Reception.objects.all()
    serializer_class = ReceptionSerializer


class LoginPageView(TemplateView):
    template_name = 'diaweb/login.html'
