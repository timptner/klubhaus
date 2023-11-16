# Klubhaus

> Klubhaus is a platform for all students at the Faculty for Mechanical Engineering at the Otto von Guericke 
University Magdeburg to participate on a variety of offers organized by the student council.

This repository contains the source code for [https://klubhaus.farafmb.de](klubhaus.farafmb.de).

## Development

Create a virtual environment and install all dependencies.

```shell
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

Configure your project with the example config file. Edit the config file for your needs.

```shell
cp .env.example .env
```

You need to generate a new secret key. Copy the new key into `.env`. 

```shell
python -c "from django.core.management import utils; print(utils.get_random_secret_key())"
```

Migrate database. Create a superuser for yourself.

```shell
python manage.py migrate
python manage.py createsuperuser
```

Start a development webserver.

```shell
python manage.py runserver
```

## Testing

Install coverage.

```shell
python -m pip install coverage
```

Run test coverage and generate report.

```shell
coverage run --source="." --omit="manage.py,*/*sgi.py,*/migrations/*" manage.py test
coverage html
```

## Author

Aiven Timptner
