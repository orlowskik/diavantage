import datetime
import pandas as pd
import requests
import numpy as np

months = {
    'Jan.': 1,
    'Feb.': 2,
    'Mar.': 3,
    'Apr.': 4,
    'May.': 5,
    'Jun.': 6,
    'Jul.': 7,
    'Aug.': 8,
    'Sep.': 9,
    'Oct.': 10,
    'Nov.': 11,
    'Dec.': 12,

}


url_glucose = 'http://127.0.0.1:8000/api/glucose/'
url_pressure = 'http://127.0.0.1:8000/api/bloods/'

data = pd.read_csv('glucose.csv')
blood_data = pd.read_csv('bp_log.csv')

for index, row in data.iterrows():

    date = row['Date'].split(' ')[-1].split('/')
    breakfast_date = datetime.datetime(2023, months[date[1]], int(date[0]), np.random.randint(6,12), np.random.randint(0,59))
    lunch_date = datetime.datetime(2023, months[date[1]], int(date[0]), np.random.randint(12,16), np.random.randint(0,59))
    dinner_date = datetime.datetime(2023, months[date[1]], int(date[0]), np.random.randint(17, 21), np.random.randint(0,59))

    if row['Before breakfast']:
        response = requests.post(url_glucose, data={'patient': 1, 'measurement': row['Before breakfast'], 'measurement_date': breakfast_date.strftime('%Y-%m-%dT%H:%M'), 'measurement_type': 1})
    if row['Before lunch']:
        requests.post(url_glucose, data={'patient': 1, 'measurement': row['Before lunch'], 'measurement_date': lunch_date.strftime('%Y-%m-%dT%H:%M'), 'measurement_type': 3})
    if row['Before lunch']:
        requests.post(url_glucose, data={'patient': 1, 'measurement': row['Before dinner'], 'measurement_date': dinner_date.strftime('%Y-%m-%dT%H:%M'), 'measurement_type': 5})

for index, row in blood_data.iterrows():
    response = requests.post(url_pressure, data={'patient': 1, 'systolic_pressure': row['SYS'], 'diastolic_pressure': row['DIA'], 'pulse_rate': row['Pulse'], 'measurement_date': row['Measurement Date'].replace(' ', 'T').replace('2021', '2023')})