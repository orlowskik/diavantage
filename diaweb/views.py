import json
import os

import diaweb.graphs

from abc import ABCMeta, abstractmethod
from http import HTTPMethod

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.middleware import csrf
from django.views.decorators.csrf import csrf_exempt

from django.views.generic import TemplateView
from rest_framework import viewsets, status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.decorators import api_view, renderer_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer

from diaweb.models import Patient, Physician, Address, Glucose, Blood, Reception
from diaweb.serializers import PatientSerializer, PhysicianSerializer, AddressSerializer, \
    GlucoseSerializer, BloodSerializer, ReceptionSerializer, UserSerializer

from diaweb.renderers import WebUserTemplateHTMLRenderer
from diaweb.authentication import IsAuthenticatedPostLeak
from diaweb.extra_context import import_extra_context




class BasicPageView(TemplateView):
    template_name = "diaweb/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['welcome_msg'] = import_extra_context(os.path.join(settings.STATIC_ROOT, 'diaweb/files/index_page_msg'))
        return context


class MainPageView(LoginRequiredMixin, TemplateView):
    template_name = "diaweb/main.html"
    login_url = settings.LOGIN_URL


# class UserViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer

class PatientViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

    @action(detail=False, methods=[HTTPMethod.GET, HTTPMethod.POST])
    def search_patient(self, request):
        if hasattr(request.user, 'patient'):
            return Response(status=status.HTTP_200_OK, data={'patient_id': request.user.patient.id})
        return Response(status=status.HTTP_200_OK, data={'patient_id': None})



class PhysicianViewSet(viewsets.ModelViewSet):
    queryset = Physician.objects.all()
    serializer_class = PhysicianSerializer


# class AddressViewSet(viewsets.ModelViewSet):
#     queryset = Address.objects.all()
#     serializer_class = AddressSerializer


class MeasurementViewSet(viewsets.ModelViewSet, metaclass=ABCMeta):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    @property
    @abstractmethod
    def serializer_class(self):
        pass

    @property
    @abstractmethod
    def measurement_class(self):
        pass

    def has_write_permission(self, request):
        if hasattr(self.request.user, 'patient'):
            if request.data['patient'] == str(self.request.user.patient.id):
                return True
        return False

    def has_destroy_permission(self, request):
        if hasattr(self.request.user, 'patient'):
            object_instance = self.get_object()
            if object_instance.patient == self.request.user.patient:
                return True
        return False

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'patient'):
            return self.measurement_class.objects.filter(patient=user.patient)
        if hasattr(user, 'physician'):
            patients = Patient.objects.filter(physician=user.physician)
            return self.measurement_class.objects.filter(patient__in=patients)
        raise PermissionError

    def create(self, request, *args, **kwargs):
        if self.has_write_permission(request):
                return super().create(request, *args, **kwargs)
        return Response({'error': 'No permission for this patient'}, status=status.HTTP_403_FORBIDDEN)

    def update(self, request, *args, **kwargs):
        if self.has_write_permission(request):
                return super().update(request, *args, **kwargs)
        return Response({'error': 'No permission for this patient'}, status=status.HTTP_403_FORBIDDEN)

    def partial_update(self, request, *args, **kwargs):
        if self.has_write_permission(request):
                return super().partial_update(request, *args, **kwargs)
        return Response({'error': 'No permission for this patient'}, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        if self.has_destroy_permission(request):
                return super().destroy(request, *args, **kwargs)
        return Response({'error': 'No permission for this patient'}, status=status.HTTP_403_FORBIDDEN)

class GlucoseViewSet(MeasurementViewSet):
    serializer_class = GlucoseSerializer
    measurement_class = Glucose

class BloodViewSet(MeasurementViewSet):
    serializer_class = BloodSerializer
    measurement_class = Blood



# class AppointmentViewSet(viewsets.ModelViewSet):
#     queryset = Appointment.objects.all()
#     serializer_class = AppointmentSerializer
#
#
# class ReceptionViewSet(viewsets.ModelViewSet):
#     queryset = Reception.objects.all()
#     serializer_class = ReceptionSerializer


class WebUserViewSet(viewsets.ModelViewSet, metaclass=ABCMeta):
    renderer_classes = [JSONRenderer, WebUserTemplateHTMLRenderer]
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticatedPostLeak]
    style = {'template_pack': 'rest_framework/horizontal'}
    hidden_fields = ['id']

    @property
    @abstractmethod
    def create_target(self):
        pass

    @property
    @abstractmethod
    def serializer_class(self):
        pass

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.template_name = 'diaweb/list.html'
        response.data = {'list': response.data,
                         'name': self.get_queryset().first().__class__.__name__}
        return response

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        response.template_name = 'diaweb/detail.html'
        response.data['name'] = self.get_queryset().first().__class__.__name__
        response.data['result'] = self.get_queryset().get(pk=kwargs['pk'])
        response.data['pk'] = kwargs['pk']
        return response

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            instance = serializer.save()
            result = json.dumps(self.serializer_class(instance).data, indent=4)
            return_status = status.HTTP_201_CREATED
        else:
            result = json.dumps(serializer.errors, indent=4)
            return_status = status.HTTP_400_BAD_REQUEST

        return Response(data={"result": result, 'status': return_status,
                              'serializer': self.get_serializer(),
                              'style': self.style, 'hidden_fields': self.hidden_fields,
                              'creation_view': True},
                        status=return_status, template_name='diaweb/account_detail.html')

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
            result = json.dumps(serializer.errors, indent=4)
            return_status = status.HTTP_400_BAD_REQUEST

        return Response(data={"result": result, 'status': return_status,
                              'serializer': self.get_serializer(),
                              'style': self.style, 'hidden_fields': self.hidden_fields},
                        status=return_status, template_name='diaweb/account_detail.html')

    @action(detail=True, methods=[HTTPMethod.GET, HTTPMethod.PATCH])
    def account_detail(self, request, pk, *args, **kwargs):
        kwargs['pk'] = pk
        if request.method == 'PATCH':
            response = self.partial_update(request, *args, **kwargs)
        else:
            response = self.retrieve(request, *args, **kwargs)
            response.data['result'] = json.dumps(self.get_serializer(self.get_queryset().get(pk=kwargs['pk'])).data,
                                                 indent=4)
        response.template_name = 'diaweb/account_detail.html'
        response.data['serializer'] = self.get_serializer()
        response.data['style'] = self.style
        response.data['hidden_fields'] = self.hidden_fields
        response.data['target'] = self.create_target

        return response


class PatientWebViewSet(WebUserViewSet):
    serializer_class = PatientSerializer
    hidden_fields = ['id', 'confirmed_diabetes', 'classifier_result', 'last_appointment']
    create_target = 'web-patient-list'

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'patient'):
            return Patient.objects.filter(id=user.patient.id)
        if hasattr(user, 'physician'):
            return Patient.objects.filter(physician=user.physician)

    @action(detail=True, methods=[HTTPMethod.GET])
    def measurements(self, request, pk=None, *args, **kwargs):
        if pk is None:
            raise IndexError('Patient ID required')
        pk_int = int(pk)

        if self.request.user.is_anonymous:
            return Response(data = {
                'status': status.HTTP_401_UNAUTHORIZED,
                "content": "Not logged in"},
                status=status.HTTP_401_UNAUTHORIZED, template_name='diaweb/error_page.html')
        elif hasattr(self.request.user, 'patient'):
            if self.request.user.patient.id != pk_int:
                return Response(data={
                    'status': status.HTTP_401_UNAUTHORIZED,
                    "content": "No permission for this patient's data"},
                    status=status.HTTP_401_UNAUTHORIZED, template_name='diaweb/error_page.html')

        if hasattr(self.request.user, 'physician'):
            patients = Patient.objects.filter(physician=self.request.user.physician)
            print([patient.id == pk_int for patient in patients])
            if not any(patient.id == pk_int for patient in patients):
                return Response(data={
                    'status': status.HTTP_401_UNAUTHORIZED,
                    "content": "No permission for this patient's data"},
                    status=status.HTTP_401_UNAUTHORIZED, template_name='diaweb/error_page.html')

        request.session['patient_id'] = pk

        return Response(
            data={
                'name': 'Patient',
            },
            template_name='diaweb/measurements.html',
            status=status.HTTP_200_OK)


class PhysicianWebViewSet(WebUserViewSet):
    queryset = Physician.objects.all()
    serializer_class = PhysicianSerializer
    create_target = 'web-physician-list'


@api_view(['GET'])
@renderer_classes([TemplateHTMLRenderer])
def registration_view(request, registration_type):
    template_name = 'diaweb/register.html'
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


@csrf_exempt
def get_csrf(request):
    token = csrf.get_token(request)
    response = JsonResponse({'detail': 'CSRF cookie set','CSRFToken': token})
    return response
