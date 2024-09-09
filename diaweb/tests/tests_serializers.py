import unittest
from datetime import datetime, date

from django.contrib.auth.models import User

from diaweb.models import Address, Patient
from diaweb.serializers import AddressSerializer, UserSerializer, PatientSerializer
from django.test import TestCase
from rest_framework.exceptions import ValidationError as DRFValidationError


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
            'email': 'testuser@test.com',
            'first_name': 'Test',
            'last_name': 'User'
        }

        self.user = User.objects.create(**self.user_attrs)
        self.serializer = UserSerializer(instance=self.user)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertSetEqual(set(data.keys()), {'username', 'email', 'first_name', 'last_name'})

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