import datetime

from django.db import models
from django.utils import timezone
from django.contrib.auth import User

# TODO: check that first name and last name are unique across users

class Building(models.Model):
    building_name = models.CharField(max_length=55)