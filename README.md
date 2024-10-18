#####Wymagania
Python 3.11

####Uruchomienie

Z użyciem docker-compose:
- docker-compose build
- docker-compose up
  
Ręcznie:
- pip install -r requirements.txt
- python/python3.11 manage.py makemigrations
- python/python3.11 manage.py migrate
- python/python3.11 manage.py collectstatic
- python/python3.11 manage.py loaddata db.json
- python/python3.11 manage.py runserver 0.0.0.0:8000

  W obydwu przypadkach dostępny pod adresem:
  http://localhost:8000 / http://127.0.0.1:8000

Po wczytaniu danych (loaddata db.json) dostępne konto
- username: admin
- password: admin

Pomiary dostępne u pacjenta 1. (David Davis)
