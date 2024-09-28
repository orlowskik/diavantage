import json
from datetime import date, datetime

from django.db import models, IntegrityError
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

# Create your models here.
User._meta.get_field('email')._unique = True


class Address(models.Model):
    country = models.CharField(max_length=60)
    state = models.CharField(max_length=60)
    city = models.CharField(max_length=60)
    zip_code = models.CharField(max_length=10)
    street = models.CharField(max_length=100)
    number = models.CharField(max_length=10)
    apartment = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return f'{self.street} {self.number}'

    def get_details(self):
        data = {
            'country': self.country,
            'state': self.state,
            'city': self.city,
            'zip_code': self.zip_code,
            'street': self.street,
            'number': self.number,
            'apartment': self.apartment,
        }

        return data


class Patient(models.Model):
    PREDICTIONS = {
        -1: "No Diabetes",
        0: "Not Performed",
        1: "Possible Diabetes"
    }

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birthdate = models.DateField()
    sex = models.CharField(max_length=1, choices=(('M', 'Male'), ('F', 'Female')))
    confirmed_diabetes = models.BooleanField(default=False)
    classifier_result = models.IntegerField(choices=PREDICTIONS, default=0)
    last_appointment = models.DateField(null=True, blank=True)
    address = models.OneToOneField(Address, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'

    def get_age(self):
        basis = date.today()
        if basis.month > self.birthdate.month:
            return basis.year - self.birthdate.year
        elif basis.month == self.birthdate.month:
            return basis.year - self.birthdate.year if basis.day >= self.birthdate.day else basis.year - self.birthdate.year - 1
        else:
            return basis.year - self.birthdate.year - 1

    def get_prediction(self):
        return self.PREDICTIONS[self.classifier_result]

    def get_details(self):
        data = {
            'name': f'{self.user.first_name} {self.user.last_name}',
            'email': self.user.email,
            'birthdate': self.birthdate.strftime('%d-%m-%Y'),
            'age': self.get_age(),
            'sex': self.sex,
            'address': self.address.get_details() if self.address else None,
            'diabetes': self.confirmed_diabetes,
            'prediction': self.get_prediction(),
            'last_appointment': self.last_appointment
        }

        return json.dumps(data, indent=4)

    def save(self, **kwargs):
        if self.birthdate > timezone.now().date():
            raise ValidationError('Future date restricted')
        if Physician.objects.filter(user=self.user).exists():
            raise IntegrityError
        super().save(**kwargs)


class Physician(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialty = models.CharField(max_length=60)
    phone = models.CharField(max_length=20)
    patient = models.ManyToManyField(Patient)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True, blank=True, unique=False)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name} - {self.specialty}'

    def get_details(self):
        data = {
            'name': self.__str__(),
            'email': self.user.email,
            'phone': self.phone,
            'address': self.address.get_details() if self.address else None,

        }

        return json.dumps(data, indent=4)

    def save(self, **kwargs):
        if Patient.objects.filter(user=self.user).exists():
            raise IntegrityError
        super().save(**kwargs)


class Glucose(models.Model):
    MEASUREMENT_TYPES = {
        0: 'Undefined',
        1: 'Before breakfast',
        2: 'After breakfast',
        3: 'Before lunch',
        4: 'After lunch',
        5: 'Before dinner',
        6: 'After dinner'

    }

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    measurement = models.FloatField(validators=[MinValueValidator(0)])
    measurement_type = models.IntegerField(choices=MEASUREMENT_TYPES, default=0)
    measurement_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.measurement}'

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(measurement__gte=0), name='Glucose_positive_number'),
        ]

    def save(self, **kwargs):
        if isinstance(self.measurement_date, datetime):
            if self.measurement_date > timezone.now():
                raise ValidationError('Future date restricted')
        super().save(**kwargs)


class Blood(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    systolic_pressure = models.IntegerField(validators=[MinValueValidator(0)])
    diastolic_pressure = models.IntegerField(validators=[MinValueValidator(0)])
    pulse_rate = models.IntegerField(validators=[MinValueValidator(0)])
    measurement_date = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(systolic_pressure__gte=0), name='Systolic_pressure_positive_number'),
            models.CheckConstraint(check=models.Q(diastolic_pressure__gte=0),
                                   name='Diastolic_pressure_positive_number'),
            models.CheckConstraint(check=models.Q(pulse_rate__gte=0), name='Pulse_rate_positive_number'),
        ]

    def save(self, **kwargs):
        if isinstance(self.measurement_date, datetime):
            if self.measurement_date > timezone.now():
                raise ValidationError('Future date restricted')
        super().save(**kwargs)


class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    physician = models.ForeignKey(Physician, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField()


class Reception(models.Model):
    DAYS = {
        1: "Monday",
        2: "Tuesday",
        3: "Wednesday",
        4: "Thursday",
        5: "Friday",
        6: "Saturday",
        7: "Sunday"
    }

    day = models.CharField(max_length=20, choices=DAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    physician = models.ForeignKey(Physician, on_delete=models.SET_NULL, null=True, blank=True)
