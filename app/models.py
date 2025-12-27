from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.utils import timezone
from django.contrib.auth.models import UserManager
from datetime import date

class BeerUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, null=False, blank=False)
    created_at = models.DateTimeField(default=timezone.now)
    username = models.CharField(max_length=150, blank=False, unique=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    objects = UserManager()


class Brewery(models.Model):
    name = models.CharField(max_length=150, blank=False, unique=True)
    descritpion = models.TextField()
    city = models.CharField(max_length=150)

class Beer(models.Model):
    name = models.CharField(max_length=150, blank=False, unique=True)
    descritpion = models.TextField()
    bitterness = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    degree = models.DecimalField(max_digits=3, decimal_places=2, default=0)

    brewery_id = models.ForeignKey(Brewery, on_delete=models.CASCADE)


class Drinks(models.Model):
    date = models.DateField(default=date.today)
    note = models.IntegerField(default=0)
    comment = models.TextField()

    drinker_id = models.ForeignKey(BeerUser, on_delete=models.CASCADE)
    beer_id = models.ForeignKey(Beer, on_delete=models.CASCADE)