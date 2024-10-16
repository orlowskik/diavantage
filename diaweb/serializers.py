from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from .models import Address, Patient, Physician, Glucose, Blood, Appointment, Reception, User


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']


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

    def update(self, instance, validated_data):
        if validated_data.get('address', None) is not None:
            address_data = validated_data.pop('address')
            if instance.address is None:
                address = Address.objects.create(**address_data)
                instance.address = address
            else:
                address_serializer = AddressSerializer(instance.address, data=address_data, partial=True)
                if address_serializer.is_valid(raise_exception=True):
                    address_serializer.save()

        if validated_data.get('user', None) is not None:
            user_data = validated_data.pop('user')
            user_serializer = UserSerializer(instance.user, data=user_data, partial=True)
            if user_serializer.is_valid(raise_exception=True):
                user_serializer.save()

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()

        return instance


class PhysicianSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    address = AddressSerializer(allow_null=True, required=False)

    class Meta:
        model = Physician
        exclude = ('patient',)

    def create(self, validated_data):
        print('Creating')
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data)
        if validated_data.get('address') is not None:
            address_data = validated_data.pop('address')
            address = Address.objects.create(**address_data)
            physician = Physician.objects.create(user=user, address=address, **validated_data)
        else:
            physician = Physician.objects.create(user=user, **validated_data)
        return physician

    def update(self, instance, validated_data):
        if validated_data.get('address', None) is not None:
            address_data = validated_data.pop('address')
            if instance.address is None:
                address = Address.objects.create(**address_data)
                instance.address = address
            else:
                address_serializer = AddressSerializer(instance.address, data=address_data, partial=True)
                if address_serializer.is_valid(raise_exception=True):
                    address_serializer.save()

        if validated_data.get('user', None) is not None:
            user_data = validated_data.pop('user')
            user_serializer = UserSerializer(instance.user, data=user_data, partial=True)
            if user_serializer.is_valid(raise_exception=True):
                user_serializer.save()

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()

        return instance


class GlucoseSerializer(serializers.ModelSerializer):
    patient = PrimaryKeyRelatedField(queryset=Patient.objects.all())

    class Meta:
        model = Glucose
        fields = '__all__'


class BloodSerializer(serializers.ModelSerializer):
    patient = PrimaryKeyRelatedField(queryset=Patient.objects.all())

    class Meta:
        model = Blood
        fields = '__all__'


class AppointmentSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    physician = PhysicianSerializer(read_only=True, allow_null=True, required=False)

    class Meta:
        model = Appointment
        fields = '__all__'


class ReceptionSerializer(serializers.ModelSerializer):
    physician = PrimaryKeyRelatedField(queryset=Physician.objects.all(), allow_null=True, required=False)

    class Meta:
        model = Reception
        fields = '__all__'