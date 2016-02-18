from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Airline(models.Model):
    name = models.CharField(max_length = 45)
    money = models.BigIntegerField(default = 100000000)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="airline")
