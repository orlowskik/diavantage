import unittest
import datetime
from freezegun import freeze_time


from django.contrib.auth.models import User
from django.test import TestCase

from diaweb.models import Address, Patient

# Create your tests here.


class AddressTestCase(TestCase):
    def setUp(self):
        Address.objects.create(
            country="Country",
            state="State",
            city="City",
            zip_code="12345",
            street="Street",
            number="1A",
            apartment="101"
        )

    def test_address_creation(self):
        """Test if the Address instance can be created properly"""
        address = Address.objects.get(city="City")
        self.assertEqual(address.country, 'Country')
        self.assertEqual(address.state, 'State')
        self.assertEqual(address.zip_code, '12345')
        self.assertEqual(address.street, 'Street')
        self.assertEqual(address.number, '1A')
        self.assertEqual(address.apartment, '101')

    def test_address_city(self):
        """Test if the Address city is correctly retrieved"""
        address = Address.objects.get(city="City")
        self.assertEqual(address.city, 'City')

    def test_address_country(self):
        """Test if the Address country is correctly retrieved"""
        address = Address.objects.get(country="Country")
        self.assertEqual(address.country, 'Country')

    def test_address_state(self):
        """Test if the Address state is correctly retrieved"""
        address = Address.objects.get(state="State")
        self.assertEqual(address.state, 'State')

class TestPatientModel(TestCase):

    def setUp(self):
        self.addr = Address.objects.create(
            country='Country',
            state='State',
            city='City',
            zip_code='123456',
            street='Street',
            number='1A',
            apartment='101')

        self.user = User.objects.create_user(username='user1',
                                             email='user1@example.com',
                                             password='password',
                                             first_name='Name',
                                             last_name='Surname')
        self.patient = Patient.objects.create(user=self.user,
                                              birthdate=datetime.date(2000, 5, 5),
                                              sex='M',
                                              address=self.addr)

    def test_object_created(self):
        self.assertTrue(isinstance(self.patient, Patient))

    def test_patient_to_string_method(self):
        self.assertEqual(self.patient.__str__(), f'Name Surname')

    @freeze_time('2024-09-07')
    def test_age_method_after_birthday(self):
        age = self.patient.get_age()
        self.assertEqual(age, 24)

    @freeze_time('2024-01-07')
    def test_age_method_before_birthday_month(self):
        age = self.patient.get_age()
        self.assertEqual(age, 23)

    @freeze_time('2024-05-04')
    def test_age_method_before_birthday_day(self):
        age = self.patient.get_age()
        self.assertEqual(age, 23)

    @freeze_time('2024-05-05')
    def test_age_method_birthday(self):
        age = self.patient.get_age()
        self.assertEqual(age, 24)

    def test_diagnosis_method(self):
        diagnosis = self.patient.get_prediction()
        self.assertEqual(diagnosis, "Not Performed")