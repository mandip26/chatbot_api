# Create Virtual env
python -m venv env

# Activate the env
env/Scripts/activate

# Install 
pip install django djangorestframework

pip install -r requirements.txt

# Run mitigrations
python manage.py migrate

# Run server
python manage.py runserver
