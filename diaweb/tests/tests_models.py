import datetime

from django.core.exceptions import ValidationError
from freezegun import freeze_time


from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from diaweb.models import Address, Patient, Physician, Glucose, Blood, Reception, Appointment


# Create your tests here.
class DataProvider:
    def __init__(self):
        self.user1 = User.objects.create_user(username='testuser1', first_name='test1', last_name='user1', email='user1@test.com', password='<PASSWORD>')
        self.user2 = User.objects.create_user(username='testuser2', first_name='test2', last_name='user2', email='user2@test.com', password='<PASSWORD>')
        self.address = Address.objects.create(
            country="Country",
            state="State",
            city="City",
            zip_code="12345",
            street="Street",
            number="1A",
            apartment="101"
        )
        self.patient = self.patient = Patient.objects.create(
                                              user=User.objects.create_user(username='testuser3',email='user3@test.com',password='<PASSWORD>'),
                                              birthdate=datetime.date(2000, 5, 5),
                                              sex='M',
                                              )

        self.physician = Physician.objects.create(user=User.objects.create_user(username='testuser4', email='user4@test.com', password='<PASSWORD>'), specialty='General Physician',
                                                  phone='1234567890',
                                                  )

class TestAddressModel(TestCase):
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
        self.data = DataProvider()
        self.patient = Patient.objects.create(user=self.data.user1,
                                              birthdate=datetime.date(2000, 5, 5),
                                              sex='M',
                                              address=self.data.address)

    def test_object_created(self):
        self.assertTrue(isinstance(self.patient, Patient))

    def test_patient_to_string_method(self):
        self.assertEqual(self.patient.__str__(), f'{self.data.user1.first_name} {self.data.user1.last_name}')

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

    def test_future_birthday_validation(self):
        with self.assertRaises(ValidationError):
            Patient.objects.create(user=self.data.user1, sex='M', birthdate=timezone.now().date()+datetime.timedelta(days=1))


    def test_diagnosis_method(self):
        diagnosis = self.patient.get_prediction()
        self.assertEqual(diagnosis, "Not Performed")

    def test_address_relationship(self):
        self.assertTrue(hasattr(self.patient, 'address'))
        self.assertEqual(self.patient.address.street, self.data.address.street)
        self.assertEqual(self.patient.address.city, self.data.address.city)
        self.assertEqual(self.patient.address.zip_code, self.data.address.zip_code)
        self.assertEqual(self.patient.address.country, self.data.address.country)
        self.assertEqual(self.patient.address.state, self.data.address.state)
        self.assertEqual(self.patient.address.number, self.data.address.number)
        self.assertEqual(self.patient.address.apartment, self.data.address.apartment)

    def test_patient_unique_user(self):
        with self.assertRaises(IntegrityError):
            Patient.objects.create(user=self.data.user1, birthdate=datetime.date(2000,1,1), sex='F' )

    def test_patient_unique_user_physician(self):
        Physician.objects.create(user=self.data.user2, specialty='General Physician', phone='1234567890',)
        with self.assertRaises(IntegrityError):
            Patient.objects.create(user=self.data.user2, birthdate=datetime.date(2000, 5, 5),
                                   sex='M',)

class TestPhysicianModel(TestCase):

    def setUp(self):
        self.data = DataProvider()
        self.specialty = 'General Physician'
        self.phone = '1234567890'
        self.physician = Physician.objects.create(user=self.data.user1, specialty=self.specialty, phone=self.phone,
                                                  address=self.data.address)
        self.physician.patient.add(self.data.patient)

    def test_physician_creation(self):
        self.assertTrue(isinstance(self.physician, Physician))
        self.assertEqual(self.physician.user.username, 'testuser1')
        self.assertEqual(self.physician.specialty, self.specialty)
        self.assertEqual(self.physician.phone, self.phone)
        self.assertEqual(self.physician.address.street, self.data.address.street)
        self.assertEqual(self.physician.address.city, self.data.address.city)
        self.assertEqual(self.physician.address.zip_code, self.data.address.zip_code)

    def test_physician_to_string_method(self):
        self.assertEqual(str(self.physician), f'{self.data.user1.first_name} {self.data.user1.last_name} - {self.specialty}')

    def test_physician_patient_relationship(self):
        self.assertTrue(self.physician.patient.exists())
        self.assertEqual(self.physician.patient.first().sex, 'M')
        self.assertEqual(self.physician.patient.first().user.username, 'testuser3')

    def test_physician_unique_user(self):
        with self.assertRaises(IntegrityError):
            Physician.objects.create(user=self.data.user1, specialty=self.specialty, phone=self.phone,
                                    address=self.data.address)

    def test_physician_unique_user_patient(self):
        with self.assertRaises(IntegrityError):
            Physician.objects.create(user=self.data.patient.user, specialty=self.specialty, phone=self.phone)

class TestGlucoseModel(TestCase):

    def setUp(self):
        self.data = DataProvider()
        self.glucose = Glucose.objects.create(patient=self.data.patient, measurement=5.6, measurement_date=timezone.now())

    def test_create_glucose(self):
        self.assertEqual(self.glucose.measurement, 5.6)
        self.assertEqual(self.glucose.patient, self.data.patient)
        self.assertIsNotNone(self.glucose.measurement_date)

    def test_glucose_str(self):
        self.assertEqual(str(self.glucose), str(self.glucose.measurement))

    def test_glucose_has_patient(self):
        self.assertTrue(hasattr(self.glucose, 'patient'))

    def test_glucose_has_measurement(self):
        self.assertTrue(hasattr(self.glucose, 'measurement'))

    def test_glucose_has_measurement_date(self):
        self.assertTrue(hasattr(self.glucose, 'measurement_date'))

    def test_glucose_without_patient(self):
        with self.assertRaises(IntegrityError):
            Glucose.objects.create(measurement=5.6, measurement_date=timezone.now())

    def test_glucose_without_measurement(self):
        with self.assertRaises(IntegrityError):
            Glucose.objects.create(patient=self.data.patient, measurement_date=timezone.now())

    def test_glucose_without_measurement_date(self):
        with self.assertRaises(IntegrityError):
            Glucose.objects.create(patient=self.data.patient, measurement=5.6)

    def test_glucose_future_date_validation(self):
        with self.assertRaises(ValidationError):
            Glucose.objects.create(patient=self.data.patient, measurement=5.6, measurement_date=timezone.now()+datetime.timedelta(days=1))

    def test_glucose_positive_measurement_value(self):
        with self.assertRaises(IntegrityError):
            Glucose.objects.create(patient=self.data.patient, measurement=-5.6, measurement_date=timezone.now())

@freeze_time('2024-01-07')
class TestBloodModel(TestCase):

    def setUp(self):
        self.data = DataProvider()
        self.blood = Blood.objects.create(patient=self.data.patient,
                                          systolic_pressure=120,
                                          diastolic_pressure=80,
                                          pulse_rate=60,)

    def test_blood_creation(self):
        self.assertTrue(isinstance(self.blood, Blood))

    def test_systolic_pressure(self):
        self.assertEqual(self.blood.systolic_pressure, 120)

    def test_diastolic_pressure(self):
        self.assertEqual(self.blood.diastolic_pressure, 80)

    def test_pulse_rate(self):
        self.assertEqual(self.blood.pulse_rate, 60)

    def test_measurement_date_creation(self):
        self.assertIsNotNone(self.blood.measurement_date)
        self.assertEqual(str(self.blood.measurement_date), '2024-01-07 00:00:00+00:00')

    def test_patient_existence(self):
        self.assertEqual(self.blood.patient.id, self.data.patient.id)
        self.assertEqual(self.blood.patient.user.first_name, self.data.patient.user.first_name)

    def test_blood_systolic_pressure_validation(self):
        with self.assertRaises(IntegrityError):
            Blood.objects.create(patient=self.data.patient,
                                 systolic_pressure=-119,
                                 diastolic_pressure=80,
                                 pulse_rate=60,)

    def test_blood_diastolic_pressure_validation(self):
        with self.assertRaises(IntegrityError):
            Blood.objects.create(patient=self.data.patient,
                                 systolic_pressure=119,
                                 diastolic_pressure=-80,
                                 pulse_rate=60,)

    def test_blood_pulse_ratio_validation(self):
        with self.assertRaises(IntegrityError):
            Blood.objects.create(patient=self.data.patient,
                                 systolic_pressure=119,
                                 diastolic_pressure=80,
                                 pulse_rate=-60,)

    def test_blood_measurement_date_validation(self):
        with self.assertRaises(ValidationError):
            Blood.objects.create(patient=self.data.patient,
                                 systolic_pressure=119,
                                 diastolic_pressure=80,
                                 pulse_rate=60,
                                 measurement_date=timezone.now()+datetime.timedelta(days=1)
                                 )

class TestReceptionModel(TestCase):

    def setUp(self):
        self.data = DataProvider()

    def test_create_reception(self):
        reception = Reception.objects.create(
            day=datetime.date.today(),
            start_time=datetime.time(hour=9, minute=0),
            end_time=datetime.time(hour=17, minute=0),
            physician=self.data.physician
        )

        self.assertEqual(reception.day, datetime.date.today())
        self.assertEqual(reception.start_time, datetime.time(hour=9, minute=0))
        self.assertEqual(reception.end_time, datetime.time(hour=17, minute=0))
        self.assertEqual(reception.physician, self.data.physician)

    def test_create_reception_with_no_physician(self):
        reception = Reception.objects.create(
            day=datetime.date.today(),
            start_time=datetime.time(hour=9, minute=0),
            end_time=datetime.time(hour=17, minute=0),
            physician=None
        )

        self.assertEqual(reception.day, datetime.date.today())
        self.assertEqual(reception.start_time, datetime.time(hour=9, minute=0))
        self.assertEqual(reception.end_time, datetime.time(hour=17, minute=0))
        self.assertIsNone(reception.physician)

    def test_physician_deletion_sets_reception_physician_to_null(self):
        physician = Physician.objects.create(user=User.objects.create_user(username='testuser5', email='user5@test.com', password='<PASSWORD>'),
                                             specialty='General Physician',
                                             phone='1234567890',
                                             )

        reception = Reception.objects.create(
            day=datetime.date.today(),
            start_time=datetime.time(hour=9, minute=0),
            end_time=datetime.time(hour=17, minute=0),
            physician=physician
        )

        physician.delete()
        reception.refresh_from_db()

        self.assertIsNone(reception.physician)

class TestAppointmentModel(TestCase):

    def setUp(self):
        self.data = DataProvider()

    def test_appointment_creation(self):
        appointment = Appointment.objects.create(patient=self.data.patient, physician=self.data.physician, date=timezone.now())
        self.assertIsInstance(appointment, Appointment)
        self.assertEqual(appointment.patient.user, self.data.patient.user)
        self.assertEqual(appointment.physician.user, self.data.physician.user)

    def test_appointment_date(self):
        now = timezone.now()
        appointment = Appointment.objects.create(patient=self.data.patient, physician=self.data.physician, date=now)
        self.assertEqual(appointment.date, now)

    def test_on_delete_cascade_patient(self):
        patient = self.patient = Patient.objects.create(
            user=User.objects.create_user(username='testuser', email='user3@test.com', password='<PASSWORD>'),
            birthdate=datetime.date(2000, 5, 5),
            sex='M',
        )
        appointment = Appointment.objects.create(patient=patient, physician=self.data.physician, date=timezone.now())
        self.assertEqual(appointment.patient.user.username, 'testuser')
        patient.delete()
        with self.assertRaises(Appointment.DoesNotExist):
            Appointment.objects.get(id=appointment.id)

    def test_on_delete_set_null_physician(self):
        physician = Physician.objects.create(
            user=User.objects.create_user(username='testuser5', email='user5@test.com', password='<PASSWORD>'),
            specialty='General Physician',
            phone='1234567890',
            )
        appointment = Appointment.objects.create(patient=self.data.patient, physician=physician, date=timezone.now())
        self.assertEqual(appointment.physician.user.username, 'testuser5')
        physician.delete()
        appointment.refresh_from_db()
        self.assertEqual(appointment.physician, None)

