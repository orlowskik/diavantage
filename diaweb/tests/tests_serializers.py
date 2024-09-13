import unittest
from datetime import datetime, date, timedelta

from django.contrib.auth.models import User
from django.utils import timezone

from diaweb.models import Address, Patient, Physician, Glucose, Blood
from diaweb.serializers import AddressSerializer, UserSerializer, PatientSerializer, PhysicianSerializer, \
    GlucoseSerializer, BloodSerializer
from django.test import TestCase
from rest_framework.exceptions import ValidationError as DRFValidationError

from diaweb.tests.tests_models import DataProvider

class AddressSerializerTestCase(TestCase):

    def setUp(self):
        self.address_info = {
            'id': 1,
            "country": "United States",
            "state": "New York",
            "city": "New York",
            "zip_code": "10003",
            "street": "2nd Street",
            'number': '1',
            'apartment': 'A'
        }
        """
        Set up the dependencies for the tests.
        """
        self.address = Address.objects.create(**self.address_info)

    def test_address_serializer_data(self):
        """
        Test Address Serializer Data
        """
        serializer = AddressSerializer(instance=self.address)
        self.assertEqual(serializer.data, self.address_info)

    def test_address_serializer_invalid_data(self):
        """
        Test Address Serializer Invalid Data
        """
        invalid_address_info = {
            "street": "",
            "city": "New York",
            "state": "New York",
            "zipcode": "10003"
        }
        serializer = AddressSerializer(data=invalid_address_info)
        self.assertRaises(DRFValidationError, serializer.is_valid, raise_exception=True)

    def test_address_serializer_save(self):
        """
        Test Address Serializer Full Update
        """
        data = {
            'id': 2,
            "country": "United States",
            "state": "New York",
            "city": "New York",
            "zip_code": "10003",
            "street": "3nd Street",
            'number': '13',
            'apartment': 'A'
        }
        serializer = AddressSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        address = serializer.save()
        self.assertIsInstance(address, Address)
        self.address.refresh_from_db()
        self.assertEqual(address.street, data['street'])

class TestUserSerializer(TestCase):
    def setUp(self):
        # Create a user instance
        self.user_attrs = {
            'username': 'testuser',
            'password': '<PASSWORD>',
            'email': 'testuser@test.com',
            'first_name': 'Test',
            'last_name': 'User'
        }

        self.user = User.objects.create(**self.user_attrs)
        self.serializer = UserSerializer(instance=self.user)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertSetEqual(set(data.keys()), {'username', 'email', 'password', 'first_name', 'last_name'})

    def test_field_content(self):
        data = self.serializer.data
        for field in ['username', 'email', 'first_name', 'last_name']:
            self.assertEqual(data[field], self.user_attrs[field])

    def test_user_save(self):
        self.user.delete()
        self.serializer = UserSerializer(data=self.user_attrs)
        self.assertTrue(self.serializer.is_valid(raise_exception=True))
        self.user = self.serializer.save()
        self.assertIsInstance(self.user, User)
        self.assertEqual(self.user.username, self.user_attrs['username'])


    def test_same_user_save(self):
        serializer = UserSerializer(data=self.user_attrs)
        with self.assertRaises(DRFValidationError):
            self.assertTrue(serializer.is_valid(raise_exception=True))

    def test_same_username(self):
        data = {
            'username': 'testuser',
            'email': 'testuser1@test.com',
            'first_name': 'Test1',
            'last_name': 'User1'
        }
        serializer = UserSerializer(data=data)
        with self.assertRaises(DRFValidationError):
            serializer.is_valid(raise_exception=True)

    def test_same_email(self):
        data = {
            'username': 'testuser1',
            'email': 'testuser@test.com',
            'first_name': 'Test1',
            'last_name': 'User1'
        }
        serializer = UserSerializer(data=data)
        with self.assertRaises(DRFValidationError):
            serializer.is_valid(raise_exception=True)


    def test_invalid_user_save(self):
        self.user.delete()
        self.user_attrs['username'] = ''
        self.serializer = UserSerializer(data=self.user_attrs)
        self.assertFalse(self.serializer.is_valid())
        with self.assertRaises(AssertionError):
            self.serializer.save()



class TestPatientSerializer(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='<PASSWORD>',
            email='user@example.com',
            first_name='Test',
            last_name='User')

        self.address = Address.objects.create(
            country= "United States",
            state= "New York",
            city= "New York",
            zip_code= "10003",
            street= "2nd Street",
            number= '1',
            apartment= 'A'
        )

        self.patient = Patient.objects.create(
            user=self.user,
            address=self.address,
            birthdate=date(2000, 1, 1),
            sex='M',
        )

        self.user_data = UserSerializer(self.user).data
        self.address_data = AddressSerializer(self.address).data
        self.patient_data = {
            'user': self.user_data,
            'address': self.address_data,
            'birthdate': '2000-01-01',
            'sex': 'M',
        }

    def test_contains_expected_fields(self):

        serializer = PatientSerializer(instance=self.patient)
        data = serializer.data
        self.assertEqual(set([field.name for field in Patient._meta.fields]), set(data.keys()))

    def test_patient_field_content(self):
        serializer = PatientSerializer(instance=self.patient)
        data = serializer.data

        tmp = set([field.name for field in Patient._meta.fields]).difference({'user', 'address'})
        for field in tmp:
            if field == 'birthdate':
                self.assertEqual(data[field], self.patient.__dict__[field].strftime('%Y-%m-%d'))
            else:
                self.assertEqual(data[field], self.patient.__dict__[field])


    def test_patient_save(self):
        self.patient.delete()
        self.address.delete()
        self.user.delete()

        serializer = PatientSerializer(data=self.patient_data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        self.assertIsInstance(patient := serializer.save(), Patient)

        self.assertEqual(patient.user.username, self.user_data['username'])
        self.assertEqual(patient.user.email, self.user_data['email'])
        self.assertEqual(patient.address.country, self.address_data['country'])
        self.assertEqual(patient.address.apartment, self.address_data['apartment'])


class TestPhysicianSerializer(TestCase):
    def setUp(self):
        self.data = DataProvider()
        self.serializer = PhysicianSerializer(instance=self.data.physician)

    def test_invalid_serializer(self):
        invalid_data = self.serializer.data.pop('user')
        self.serializer = PhysicianSerializer(data=invalid_data)
        self.assertFalse(self.serializer.is_valid())

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertCountEqual(data.keys(), set([field.name for field in Physician._meta.fields]))

    def test_valid_serializer_without_address(self):
        data = self.serializer.data
        self.data.physician.user.delete()
        self.data.physician.delete()
        self.serializer = PhysicianSerializer(data=data)
        self.assertTrue(self.serializer.is_valid(raise_exception=True))
        self.assertIsInstance(physician := self.serializer.save(), Physician)
        self.data.physician = physician
        self.assertEqual(physician.user.username, data.get('user').get('username'))

    def test_valid_serializer_with_address(self):
        data = self.serializer.data
        data['address'] = AddressSerializer(instance=self.data.address).data
        self.data.physician.user.delete()
        self.data.physician.delete()
        self.serializer = PhysicianSerializer(data=data)
        self.assertTrue(self.serializer.is_valid(raise_exception=True))
        self.assertIsInstance(physician := self.serializer.save(), Physician)
        self.assertEqual(physician.address.city, self.data.address.city)
        self.assertEqual(physician.address.apartment, self.data.address.apartment)


class TestGlucoseSerializer(TestCase):

    def setUp(self):
        self.data = DataProvider()

    def test_glucose_create(self):
        patient = Patient.objects.create(user=self.data.user1, birthdate=date(2000,1,1), sex='M')
        data = {
            'patient': patient.id,
            'measurement': 120,
            'measurement_date': timezone.now()
        }
        serializer = GlucoseSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertIsInstance(glucose := serializer.save(), Glucose)
        self.assertEqual(data['patient'], glucose.patient.id)
        self.assertEqual(data['measurement'], glucose.measurement)
        self.assertEqual(data['measurement_date'], glucose.measurement_date)

    def test_invalid_patient(self):
        data = {
            'patient': 99,
            'measurement': 120,
            'measurement_date': timezone.now()
        }
        serializer = GlucoseSerializer(data=data)
        with self.assertRaises(DRFValidationError):
            serializer.is_valid(raise_exception=True)

    def test_patient_field_is_required(self):
        data = {
            'measurement': 8,
            'measurement_date': timezone.now()
        }
        serializer = GlucoseSerializer(data=data)
        with self.assertRaises(DRFValidationError):
            serializer.is_valid(raise_exception=True)

    def test_reading_value_field_is_required(self):
        patient = Patient.objects.create(user=self.data.user1, birthdate=date(2000,1,1), sex='M')
        data = {
            'patient': patient.id,
            'measurement_date': timezone.now()
        }
        serializer = GlucoseSerializer(data=data)
        with self.assertRaises(DRFValidationError):
            serializer.is_valid(raise_exception=True)


class TestBloodSerializer(TestCase):

    def setUp(self):
        self.data = DataProvider()

    def test_blood_create(self):
        data = {
            "patient" : self.data.patient.id,
            "systolic_pressure" : 120,
            "diastolic_pressure" : 70,
            "pulse_rate" : 140,
            "measurement_date" : timezone.now()
        }

        serializer = BloodSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertIsInstance(blood := serializer.save(), Blood)
        self.assertEqual(data['patient'], blood.patient.id)
        self.assertEqual(data['measurement_date'], blood.measurement_date)

    def test_invalid_patient(self):
        data = {
            'patient': 99,
            "systolic_pressure" : 120,
            "diastolic_pressure" : 70,
            "pulse_rate" : 140,
            "measurement_date" : timezone.now()
        }
        serializer = BloodSerializer(data=data)
        with self.assertRaises(DRFValidationError):
            serializer.is_valid(raise_exception=True)

    def test_patient_field_is_required(self):
        data = {
            "systolic_pressure" : 120,
            "diastolic_pressure" : 70,
            "pulse_rate" : 140,
            "measurement_date" : timezone.now()
        }
        serializer = BloodSerializer(data=data)
        with self.assertRaises(DRFValidationError):
            serializer.is_valid(raise_exception=True)

    def test_systolic_field_is_required(self):
        data = {
            'patient': self.data.patient.id,
            "diastolic_pressure" : 70,
            "pulse_rate" : 140,
            "measurement_date" : timezone.now()
        }
        serializer = BloodSerializer(data=data)
        with self.assertRaises(DRFValidationError):
            serializer.is_valid(raise_exception=True)

    def test_diastolic_field_is_required(self):
        data = {
            'patient': self.data.patient.id,
            "systolic_pressure": 70,
            "pulse_rate": 140,
            "measurement_date": timezone.now()
        }
        serializer = BloodSerializer(data=data)
        with self.assertRaises(DRFValidationError):
            serializer.is_valid(raise_exception=True)

    def test_pulse_field_is_required(self):
        data = {
            'patient': self.data.patient.id,
            "diastolic_pressure": 70,
            "systolic_pressure": 70,
            "measurement_date": timezone.now()
        }
        serializer = BloodSerializer(data=data)
        with self.assertRaises(DRFValidationError):
            serializer.is_valid(raise_exception=True)