from rest_framework import serializers
from .models import Address, Patient, Physician, Glucose, Blood, Appointment, Reception, User


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']


class PatientSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    address = AddressSerializer()

    class Meta:
        model = Patient
        fields = '__all__'


    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data)
        address_data = validated_data.pop('address')
        address = Address.objects.create(**address_data)
        patient = Patient.objects.create(user=user, address=address, **validated_data)
        return patient


class PhysicianSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    address = AddressSerializer()

    class Meta:
        model = Physician
        exclude = ('patient',)

class GlucoseSerializer(serializers.ModelSerializer):
    patient = PatientSerializer()

    class Meta:
        model = Glucose
        fields = '__all__'


class BloodSerializer(serializers.ModelSerializer):
    patient = PatientSerializer()

    class Meta:
        model = Blood
        fields = '__all__'


class AppointmentSerializer(serializers.ModelSerializer):
    patient = PatientSerializer()
    physician = PhysicianSerializer()

    class Meta:
        model = Appointment
        fields = '__all__'


class ReceptionSerializer(serializers.ModelSerializer):
    physician = PhysicianSerializer()

    class Meta:
        model = Reception
        fields = '__all__'