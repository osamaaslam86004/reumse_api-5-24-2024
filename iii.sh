echo "BUILD START"
python3.9 -m pip install --no-cache-dir --disable-pip-version-check -r requirements.txt
# python3.11 manage.py makemigrations --noinput
# python3.11 manage.py migrate --noinput
echo "BUILD END"
