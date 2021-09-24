from django.contrib.gis.db import models
from django.contrib.postgres.search import SearchVectorField
from model_utils import Choices
from phonenumber_field.modelfields import PhoneNumberField


class Voter(models.Model):
    ZONE = Choices(
        (1, 'one', 'Zone One'),
        (2, 'two', 'Zone Two'),
        (3, 'three', 'Zone Three'),
        (4, 'four', 'Zone Four'),
        (5, 'five', 'Zone Five'),
    )
    PARTY = Choices(
        (10, 'unaffiliated', 'Unaffiliated'),
        (20, 'republican', 'Republican'),
        (30, 'democratic', 'Democratic'),
        (40, 'libertarian', 'Libertarian'),
        (50, 'constitution', 'Constitution'),
    )
    GENDER = Choices(
        (10, 'male', 'Male'),
        (20, 'female', 'Female'),
        (30, 'unknown', 'Unknown'),
    )
    voter_id = models.IntegerField(
        blank=False,
    )
    name = models.CharField(
        max_length=255,
        blank=True,
        default='',
        editable=True,
    )
    address = models.CharField(
        max_length=255,
        blank=True,
        default='',
        editable=True,
    )
    location = models.CharField(
        max_length=255,
        blank=True,
        default='',
        editable=True,
    )
    phone = PhoneNumberField(
        blank=False,
        null=True,
    )
    place = models.CharField(
        max_length=255,
        blank=True,
        default='',
        editable=True,
    )
    point = models.PointField(
        null=True,
        blank=True,
    )
    is_precise = models.BooleanField(
        default=False,
    )
    prefix = models.CharField(
        max_length=100,
        blank=True,
    )
    last_name = models.CharField(
        max_length=100,
        blank=False,
    )
    first_name = models.CharField(
        max_length=100,
        blank=False,
    )
    middle_name = models.CharField(
        max_length=100,
        blank=True,
    )
    suffix = models.CharField(
        max_length=100,
        blank=True,
    )
    age = models.IntegerField(
        blank=False,
    )
    street = models.CharField(
        max_length=100,
        blank=False,
    )
    city = models.CharField(
        max_length=100,
        blank=False,
    )
    st = models.CharField(
        max_length=2,
        blank=False,
    )
    zipcode = models.CharField(
        max_length=5,
        blank=False,
    )
    gender = models.IntegerField(
        blank=True,
        choices=GENDER,
        null=True,
    )
    zone = models.IntegerField(
        blank=False,
        choices=ZONE,
        null=True,
    )
    party = models.IntegerField(
        blank=False,
        choices=PARTY,
        null=True,
    )
    registration = models.DateField(
        null=True,
    )
    precinct = models.IntegerField(
        blank=False,
        null=True,
    )
    geocode = models.JSONField(
        blank=True,
        null=True,
    )
    search_vector = SearchVectorField(
        null=True,
        blank=True,
    )
    created = models.DateTimeField(
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def natural_key(self):
        return (self.voter_id)
