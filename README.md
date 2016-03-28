# Open Airline Manager [![Build Status](https://travis-ci.org/Dunstark/open_airline_manager.svg?branch=master)](https://travis-ci.org/Dunstark/open_airline_manager) [![Coverage Status](https://coveralls.io/repos/github/Dunstark/open_airline_manager/badge.svg?branch=master)](https://coveralls.io/github/Dunstark/open_airline_manager?branch=master)

Open Airline Manager is a game built on Django where players can manage an airline and compete with each other.

## Requirements
You need to have the following to install Open Airline Manager:
* Python 3.5+
* Django (1.8.x or 1.9.x)
* A PostgreSQL database(9.5+), with Psycopg2
* django-widget-tweaks
* django-gravatar2

## Installation
Install Open Airline Manager as you would any Django App on your server.

Do not forget to add the following to your `INSTALLED_APPS`:
```python
'airline_manager',
'widget_tweaks',
'django_gravatar',
```

You should also set up a Cron Job (or your system's equivalent).
In your terminal type:

```
crontab -e
```
And then add:
```
* 1 * * * /path/to/your/ranking.py
```

This will allow you to compute your players stats daily (at 1a.m.)