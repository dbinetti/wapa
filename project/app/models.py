# First-Party
from address.models import AddressField
from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from hashid_field import HashidAutoField
from model_utils import Choices

# Local
from .managers import UserManager

# from model_utils import Choices



class Account(models.Model):
    id = HashidAutoField(
        primary_key=True,
    )
    name = models.CharField(
        max_length=100,
        blank=False,
    )
    is_steering = models.BooleanField(
        default=False,
    )
    is_public = models.BooleanField(
        default=False,
    )
    address = AddressField(
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    notes = models.TextField(
        max_length=2000,
        blank=True,
        default='',
    )
    created = models.DateTimeField(
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        auto_now=True,
    )
    user = models.OneToOneField(
        'app.User',
        on_delete=models.CASCADE,
        related_name='account',
        unique=True,
    )

    def __str__(self):
        return f"{self.name}"


class User(AbstractBaseUser):
    id = HashidAutoField(
        primary_key=True,
    )
    username = models.CharField(
        max_length=150,
        blank=False,
        null=False,
        unique=True,
    )
    data = models.JSONField(
        null=True,
        editable=False,
    )
    name = models.CharField(
        max_length=100,
        blank=True,
        default='(Unknown)',
        verbose_name="Name",
        editable=False,
    )
    email = models.EmailField(
        blank=False,
        editable=True,
    )
    is_active = models.BooleanField(
        default=True,
    )
    is_admin = models.BooleanField(
        default=False,
    )
    created = models.DateTimeField(
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        auto_now=True,
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = [
    ]

    objects = UserManager()

    @property
    def is_staff(self):
        return self.is_admin

    def __str__(self):
        return str(self.name)

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


class School(models.Model):
    id = HashidAutoField(
        primary_key=True,
    )
    name = models.CharField(
        max_length=100,
        blank=False,
    )
    created = models.DateTimeField(
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.name}"


class Student(models.Model):
    id = HashidAutoField(
        primary_key=True,
    )
    name = models.CharField(
        max_length=100,
        blank=False,
    )
    GRADE = Choices(
        (-1, 'prek', 'Pre-K'),
        (0, 'kindergarten', 'Kindergarten'),
        (1, 'first', 'First Grade'),
        (2, 'second', 'Second Grade'),
        (3, 'third', 'Third Grade'),
        (4, 'fourth', 'Fourth Grade'),
        (5, 'fifth', 'Fifth Grade'),
        (6, 'sixth', 'Sixth Grade'),
        (7, 'seventh', 'Seventh Grade'),
        (8, 'eighth', 'Eighth Grade'),
        (9, 'ninth', 'Ninth Grade'),
        (10, 'tenth', 'Tenth Grade'),
        (11, 'eleventh', 'Eleventh Grade'),
        (12, 'twelfth', 'Twelfth Grade'),
    )
    grade = models.IntegerField(
        choices=GRADE,
        blank=True,
        null=True,
    )
    account = models.ForeignKey(
        'app.Account',
        on_delete=models.CASCADE,
        related_name='students',
        null=False,
        blank=False,
    )
    school = models.ForeignKey(
        'app.School',
        on_delete=models.CASCADE,
        related_name='students',
        null=False,
        blank=False,
    )
    created = models.DateTimeField(
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.name}"
