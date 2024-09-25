import json
import os
import numpy as np

from django.conf import settings

from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.generic import TemplateView
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer, BrowsableAPIRenderer
from rest_framework.views import APIView


from diaweb.models import Patient, Physician, Address, Glucose, Blood, Appointment, Reception
from diaweb.serializers import PatientSerializer, PhysicianSerializer, AddressSerializer, \
    GlucoseSerializer, BloodSerializer, AppointmentSerializer, ReceptionSerializer
from diaweb.renderers import MyTemplateHTMLRenderer

from diaweb.extra_context import import_extra_context

class BasicPageView(TemplateView):
    template_name = "diaweb/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['welcome_msg'] = import_extra_context(os.path.join(settings.STATIC_ROOT, 'diaweb/files/index_page_msg'))
        return context


# Create your views here
class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer


# class PatientListView(ListAPIView):
#     queryset = Patient.objects.all()
#     serializer_class = PatientSerializer
#     renderer_classes = [TemplateHTMLRenderer]
#     template_name = "diaweb/patient_list.html"
#
#     def get(self, request, *args, **kwargs):
#         return Response({'serializer': self.serializer_class, 'style': {'template_pack': 'rest_framework/vertical'}})


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


class PatientWebViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    renderer_classes = [JSONRenderer, MyTemplateHTMLRenderer,  ]

    def get_queryset(self):
        return self.get_serializer(Patient.objects.all(), many=True).data

    @xframe_options_sameorigin
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            result = serializer.save()
        else:
            return Response(data={"result": json.dumps(serializer.errors, indent=4), 'status': 400}, status=status.HTTP_400_BAD_REQUEST, template_name='diaweb/creation_response.html')
        return Response(data={"result": json.dumps(self.serializer_class(result).data, indent=4), 'status': 201}, status=status.HTTP_201_CREATED, template_name='diaweb/creation_response.html',
                        )


    # def list(self, request, *args, **kwargs):
    #     serializer = self.serializer_class(self.get_queryset(), many=True)
    #     return Response(data={"result": json.dumps(serializer.data, indent=4), 'status': 200}, status=status.HTTP_200_OK,
    #                     headers={'X-Frame-Options': 'SAMEORIGIN', 'Content-Type': 'application/json'})


class PhysicianWebViewSet(viewsets.ModelViewSet):
    queryset = Physician.objects.all()
    serializer_class = PhysicianSerializer
    renderer_classes = [MyTemplateHTMLRenderer]

    @xframe_options_sameorigin
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            result = serializer.save()
        else:
            return Response(data={"result": json.dumps(serializer.errors, indent=4), 'status': 405}, status=405, template_name='diaweb/creation_response.html')
        return Response(data={"result": json.dumps(self.serializer_class(result).data, indent=4), 'status': 201}, status=201, template_name='diaweb/creation_response.html')



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
    target = 'web-patient-list'

    if registration_type == 'physician':
        serializer = PhysicianSerializer
        hidden_fields = ['id']
        name = 'Physician'
        target = 'web-physician-list'

    return Response({'serializer': serializer, 'style': style,
                         'hidden_fields': hidden_fields, 'name': name,
                         'target': target, 'registration_type': registration_type},
                    template_name=template_name)