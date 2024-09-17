from django.core.serializers import serialize
from django.shortcuts import render
from django.contrib.auth.models import User
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.generic import TemplateView
from rest_framework import viewsets
from rest_framework.decorators import action, api_view, renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView

from diaweb.models import Patient, Physician, Address, Glucose, Blood, Appointment, Reception
from diaweb.serializers import PatientSerializer, PhysicianSerializer, AddressSerializer, \
    GlucoseSerializer, BloodSerializer, AppointmentSerializer, ReceptionSerializer


class BasicPageView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "diaweb/diavantage_base.html"

    @staticmethod
    def get(request, *args, **kwargs):
        return Response()


# Create your views here
class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer


class PatientListView(ListAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "diaweb/patient_list.html"

    def get(self, request, *args, **kwargs):
        return Response({'serializer': self.serializer_class, 'style': {'template_pack': 'rest_framework/vertical'}})


class PhysicianViewSet(viewsets.ModelViewSet):
    queryset = Physician.objects.all()
    serializer_class = PhysicianSerializer

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
    template_name = 'diaweb/login_base.html'

@xframe_options_sameorigin
@api_view(['GET'])
@renderer_classes([TemplateHTMLRenderer])
def naked_login_view(request):
    return Response(template_name='diaweb/login.html')


@xframe_options_sameorigin
@api_view(['GET'])
@renderer_classes([TemplateHTMLRenderer])
def naked_registration_view(request, registration_type):
    template_name = 'diaweb/naked_registration.html'
    style = {'template_pack': 'rest_framework/vertical'}
    serializer = PatientSerializer
    hidden_fields = ['id', 'confirmed_diabetes', 'classifier_result', 'last_appointment']
    name = 'Patient'
    target = 'patient-list'

    if registration_type == 'physician':
        serializer = PhysicianSerializer
        hidden_fields = ['id']
        name = 'Physician'
        target = 'physician-list'

    return Response({'serializer': serializer, 'style': style,
                         'hidden_fields': hidden_fields, 'name': name,
                         'target': target}, template_name=template_name)