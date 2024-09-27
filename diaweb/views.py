import json
import os
from abc import ABCMeta, abstractmethod

from django.conf import settings
from django.contrib.auth.models import User
from django.http import QueryDict

from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.generic import TemplateView
from rest_framework import viewsets, status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.views import APIView


from diaweb.models import Patient, Physician, Address, Glucose, Blood, Appointment, Reception
from diaweb.serializers import PatientSerializer, PhysicianSerializer, AddressSerializer, \
    GlucoseSerializer, BloodSerializer, AppointmentSerializer, ReceptionSerializer, UserSerializer

from diaweb.extra_context import import_extra_context

class BasicPageView(TemplateView):
    template_name = "diaweb/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['welcome_msg'] = import_extra_context(os.path.join(settings.STATIC_ROOT, 'diaweb/files/index_page_msg'))
        return context

class MainPageView(TemplateView):
    template_name = "diaweb/main.html"


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# Create your views here
class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

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


class WebUserViewSet(viewsets.ModelViewSet, metaclass=ABCMeta):
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    style = {'template_pack': 'rest_framework/horizontal'}
    hidden_fields = ['id']


    @property
    @abstractmethod
    def create_target(self):
        pass

    @property
    @abstractmethod
    def queryset(self):
        pass

    @property
    @abstractmethod
    def serializer_class(self):
        pass

    def retrieve(self, request, *args, **kwargs):
        response =  super().retrieve(request, *args, **kwargs)
        response.template_name = 'diaweb/account_detail.html'
        response.data['serializer'] = self.get_serializer()
        response.data['style'] = self.style
        response.data['hidden_fields'] = self.hidden_fields
        response.data['result'] = json.dumps(self.get_serializer(self.get_queryset().get(pk=kwargs['pk'])).data,
                                             indent=4)
        return response


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            result = serializer.save()
        else:
            return Response(data={"result": json.dumps(serializer.errors, indent=4), 'status': status.HTTP_400_BAD_REQUEST,
                                  'target': self.create_target, 'serializer': self.get_serializer(),
                                  'style': self.style, 'hidden_fields': self.hidden_fields},
                            status=status.HTTP_400_BAD_REQUEST, template_name='diaweb/registration_response.html')

        return Response(data={"result": json.dumps(self.serializer_class(result).data, indent=4), 'status': status.HTTP_201_CREATED},
                        status=status.HTTP_201_CREATED, template_name='diaweb/registration_response.html')

    def partial_update(self, request, *args, **kwargs):
        data = request.data.copy()
        erase_keys = []
        for key, value in data.items():
            if value == '':
                erase_keys.append(key)

        for key in erase_keys:
            data.pop(key)
        serializer = self.get_serializer(self.get_queryset().get(pk=kwargs['pk']), data=data, partial=True)

        if serializer.is_valid():
            instance = serializer.save()
            result = json.dumps(self.serializer_class(instance).data, indent=4)
            return_status = status.HTTP_201_CREATED

        else:
            result = json.dumps(self.serializer_class(serializer.errors), indent=4)
            return_status = status.HTTP_400_BAD_REQUEST

        return Response(data={"result": result, 'status': return_status,
                              'target': self.create_target, 'serializer': self.get_serializer(),
                              'style': self.style, 'hidden_fields': self.hidden_fields},
                        status=return_status, template_name='diaweb/account_detail.html')


class PatientWebViewSet(WebUserViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    hidden_fields = ['id', 'confirmed_diabetes', 'classifier_result', 'last_appointment']
    create_target = 'web-patient-list'

class PhysicianWebViewSet(WebUserViewSet):
    queryset = Physician.objects.all()
    serializer_class = PhysicianSerializer
    create_target = 'web-physician-list'

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
def registration_view(request, registration_type):
    template_name = 'diaweb/register.html'
    style = {'template_pack': 'rest_framework/horizontal'}
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