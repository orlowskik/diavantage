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
    AppointmentViewSet, ReceptionViewSet, \
    BasicPageView, registration_view, PatientWebViewSet, PhysicianWebViewSet, MainPageView, \
    UserViewSet, get_csrf

router = routers.DefaultRouter()
router.register(r'patients', PatientViewSet)
router.register(r'physicians', PhysicianViewSet)
router.register(r'addresses', AddressViewSet)
router.register(r'glucose', GlucoseViewSet)
router.register(r'bloods', BloodViewSet)
router.register(r'appointments', AppointmentViewSet)
router.register(r'receptions', ReceptionViewSet)
router.register(r'users', UserViewSet)


web_router = routers.SimpleRouter()
web_router.register(r'patients', PatientWebViewSet, basename='web-patient')
web_router.register(r'physicians', PhysicianWebViewSet, basename='web-physician')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('rest-auth/', include('dj_rest_auth.urls')),
    path('api/', include(router.urls)),
    path('web/', include(web_router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('django_plotly_dash/', include('django_plotly_dash.urls', namespace='django_plotly_dash')),


    path('', BasicPageView.as_view(), name='index'),
    path('web/' , MainPageView.as_view() , name='main'),
    path('register/<registration_type>/' , registration_view , name='register'),
    path('get_csrf/' , get_csrf , name='get_csrf'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


