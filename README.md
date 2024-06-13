# resume_api

How to run this API:
python version : 3.11

python -m pip install -r requirements.txt
python manage.py flush
python manage.py reset_db
python manage.py clean_pyc
python manage.py makemigrations
python manage.py migrate
python manage.py createcachetable
