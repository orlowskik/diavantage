from datetime import date, datetime
from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class Address(models.Model):
    country   = models.CharField(max_length=60)
    state     = models.CharField(max_length=60)
    city      = models.CharField(max_length=60)
    zip_code   = models.CharField(max_length=10)
    street    = models.CharField(max_length=100)
    number    = models.CharField(max_length=10)
    apartment = models.CharField(max_length=10, null=True, blank=True)


class Patient(models.Model):

    PREDICTIONS = {
        -1 : "No Diabetes",
        0  : "Not Performed",
        1  : "Possible Diabetes"
    }

    user               = models.OneToOneField(User, on_delete=models.CASCADE)
    birthdate          = models.DateField()
    sex                = models.CharField(max_length=1, choices=(('M', 'Male'), ('F', 'Female')))
    confirmed_diabetes = models.BooleanField(default=False)
    classifier_result  = models.IntegerField(choices=PREDICTIONS, default=0)
    last_appointment   = models.DateField(null=True, blank=True)
    address            = models.OneToOneField(Address, on_delete=models.CASCADE, null=True, blank=True)

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

class Physician(models.Model):

    user      = models.OneToOneField(User, on_delete=models.CASCADE)
    specialty = models.CharField(max_length=60)
    phone     = models.CharField(max_length=20)
    patient   = models.ManyToManyField(Patient)
    address   = models.ForeignKey(Address, on_delete=models.CASCADE, null=True, blank=True, unique=False)


class Glucose(models.Model):

    patient          = models.ForeignKey(Patient, on_delete=models.CASCADE)
    measurement      = models.FloatField()
    measurement_date = models.DateTimeField()


class Blood(models.Model):

    patient             = models.ForeignKey(Patient, on_delete=models.CASCADE)
    systolic_pressure   = models.IntegerField()
    diastolic_pressure  = models.IntegerField()
    pulse_rate          = models.IntegerField()
    measurement_date    = models.DateTimeField()


class Appointment(models.Model):

    patient   = models.ForeignKey(Patient, on_delete=models.CASCADE)
    physician = models.ForeignKey(Physician, on_delete=models.CASCADE)
    date      = models.DateTimeField()


class Reception(models.Model):

    day = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    physician = models.ForeignKey(Physician, on_delete=models.SET_NULL, null=True, blank=True)




