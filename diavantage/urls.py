"""
URL configuration for diavantage project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers



from diaweb.views import PatientViewSet, PhysicianViewSet, AddressViewSet, GlucoseViewSet, BloodViewSet, \
    AppointmentViewSet, ReceptionViewSet, LoginPageView, \
    PatientListView, BasicPageView, naked_login_view, naked_registration_view

router = routers.DefaultRouter()
router.register(r'patients', PatientViewSet)
router.register(r'physicians', PhysicianViewSet)
router.register(r'addresses', AddressViewSet)
router.register(r'glucose', GlucoseViewSet)
router.register(r'bloods', BloodViewSet)
router.register(r'appointments', AppointmentViewSet)
router.register(r'receptions', ReceptionViewSet)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('rest-auth/', include('dj_rest_auth.urls')),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),


    path('', BasicPageView.as_view(), name='index'),
    path('login/', LoginPageView.as_view(), name='login'),
    path('naked_login/', naked_login_view, name='naked_login'),
    path('naked_registration/<registration_type>/' , naked_registration_view , name='naked-registration'),
    path('patient_list/' , PatientListView.as_view() , name='patient-list'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


