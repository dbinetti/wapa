# First-Party
import datetime

from address.models import AddressField
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models.constraints import UniqueConstraint
from django_fsm import FSMIntegerField
from django_fsm import transition
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
    is_spouse = models.BooleanField(
        default=False,
    )
    address = AddressField(
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    picture = models.ImageField(
        null=False,
        blank=False,
        default='wapa/avatar',
    )
    ZONE = Choices(
        (1, 'one', 'Zone One'),
        (2, 'two', 'Zone Two'),
        (3, 'three', 'Zone Three'),
        (4, 'four', 'Zone Four'),
        (5, 'five', 'Zone Five'),
    )
    zone = models.IntegerField(
        blank=True,
        null=True,
    )
    notes = models.TextField(
        max_length=2000,
        blank=True,
        default='',
    )
    story = models.TextField(
        max_length=5000,
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
    voter = models.OneToOneField(
        'app.Voter',
        on_delete=models.SET_NULL,
        related_name='account',
        unique=True,
        null=True,
    )

    def __str__(self):
        return f"{self.name}"


class Issue(models.Model):
    id = HashidAutoField(
        primary_key=True,
    )
    STATE = Choices(
        (-5, 'archived', 'Archived'),
        (0, 'pending', 'Pending'),
        (10, 'active', 'Active'),
    )
    state = FSMIntegerField(
        choices=STATE,
        default=STATE.pending,
    )
    name = models.CharField(
        max_length=100,
        blank=False,
    )
    description = models.TextField(
        max_length=2000,
        blank=True,
        default='',
    )
    recipient_name = models.CharField(
        max_length=100,
        blank=False,
    )
    recipient_emails = ArrayField(
        models.EmailField(
        ),
        null=True,
        blank=False,
    )
    date = models.DateField(
        default=datetime.date.today,
    )
    created = models.DateTimeField(
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        auto_now=True,
    )
    def __str__(self):
        return f"{self.name}"


class Isat(models.Model):
    id = HashidAutoField(
        primary_key=True,
    )
    SUBJECT = Choices(
        (10, 'english', 'English'),
        (20, 'math', 'Math'),
        (30, 'science', 'Science'),
    )
    subject = models.IntegerField(
        choices=SUBJECT,
        null=True,
    )
    GRADE = Choices(
        (1, 'all', 'All'),
        (3, 'third', 'Third'),
        (4, 'fourth', 'Fourth Grade'),
        (5, 'fifth', 'Fifth Grade'),
        (6, 'sixth', 'Sixth Grade'),
        (7, 'seventh', 'Seventh Grade'),
        (8, 'eighth', 'Eighth Grade'),
        (10, 'high', 'High School'),
    )
    grade = models.IntegerField(
        choices=GRADE,
        null=True,
    )
    advanced_note = models.CharField(
        max_length=10,
        blank=True,
    )
    proficient_note = models.CharField(
        max_length=10,
        blank=True,
    )
    basic_note = models.CharField(
        max_length=10,
        blank=True,
    )
    below_note = models.CharField(
        max_length=10,
        blank=True,
    )
    advanced = models.FloatField(
        null=True,
        blank=True,
    )
    proficient = models.FloatField(
        null=True,
        blank=True,
    )
    basic = models.FloatField(
        null=True,
        blank=True,
    )
    below = models.FloatField(
        null=True,
        blank=True,
    )
    year = models.IntegerField(
        null=False,
        blank=False,
    )
    school = models.ForeignKey(
        'app.School',
        on_delete=models.CASCADE,
        related_name='isats',
        null=True,
        blank=False,
    )
    created = models.DateTimeField(
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        auto_now=True,
    )
    def __str__(self):
        return f"{self.id}"


class Event(models.Model):
    id = HashidAutoField(
        primary_key=True,
    )
    name = models.CharField(
        max_length=100,
        blank=False,
    )
    description = models.TextField(
        max_length=2000,
        blank=True,
        default='',
    )
    date = models.DateField(
        default=datetime.date.today,
    )
    datetime = models.DateTimeField(
        null=True,
        blank=False,
    )
    location = models.CharField(
        max_length=100,
        blank=True,
        default='',
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

    def __str__(self):
        return f"{self.name}"


class School(models.Model):
    id = HashidAutoField(
        primary_key=True,
    )
    full = models.CharField(
        max_length=100,
        blank=False,
    )
    name = models.CharField(
        max_length=100,
        blank=False,
    )
    school_id = models.IntegerField(
        null=True,
        blank=True,
    )
    KIND = Choices(
        (10, 'elementary', 'Elementary School'),
        (20, 'middle', 'Middle School'),
        (30, 'high', 'High School'),
    )
    kind = models.IntegerField(
        choices=KIND,
        default=0,
    )
    created = models.DateTimeField(
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = (
            'name',
        )


class Comment(models.Model):
    id = HashidAutoField(
        primary_key=True,
    )
    STATE = Choices(
        (-10, 'denied', 'Denied'),
        (-5, 'archived', 'Archived'),
        (0, 'pending', 'Pending'),
        (10, 'approved', 'Approved'),
    )
    state = FSMIntegerField(
        choices=STATE,
        default=STATE.pending,
    )
    is_featured = models.BooleanField(
        default=False,
    )
    content = models.TextField(
        max_length=2000,
        blank=False,
    )
    account = models.ForeignKey(
        'app.Account',
        on_delete=models.CASCADE,
        related_name='comments',
        null=False,
        blank=False,
    )
    issue = models.ForeignKey(
        'app.Issue',
        on_delete=models.CASCADE,
        related_name='comments',
        null=False,
        blank=False,
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=[
                    'account',
                    'issue',
                ],
                name='unique_comment',
            )
        ]

    @property
    def wordcount(self):
        words = self.content.split(" ")
        return len(words)

    created = models.DateTimeField(
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.account.name}"

    @transition(field=state, source=[STATE.pending, STATE.denied], target=STATE.approved)
    def approve(self):
        from .tasks import send_approval_email
        from .tasks import send_super_email
        send_approval_email.delay(self.account)
        send_super_email.delay(self)
        return

    @transition(field=state, source=[STATE.pending, STATE.approved], target=STATE.denied)
    def deny(self):
        from .tasks import send_denial_email
        send_denial_email.delay(self.account)
        return


class Student(models.Model):
    id = HashidAutoField(
        primary_key=True,
    )
    name = models.CharField(
        max_length=100,
        blank=True,
        default='',
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
        blank=False,
        null=False,
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

    @property
    def ord(self):
        mapping = {
            -1: 'PK',
            0: 'K',
            1: '1st',
            2: '2nd',
            3: '3rd',
            4: '4th',
            5: '5th',
            6: '6th',
            7: '7th',
            8: '8th',
            9: '9th',
            10: '10th',
            11: '11th',
            12: '12th',
        }
        return mapping[self.grade]

    class Meta:
        ordering = (
            'grade',
        )


    def __str__(self):
        return f"{self.name}"


class Attendee(models.Model):
    id = HashidAutoField(
        primary_key=True,
    )
    is_confirmed = models.BooleanField(
        default=False,
    )
    account = models.ForeignKey(
        'app.Account',
        on_delete=models.CASCADE,
        related_name='attendees',
        null=False,
        blank=False,
    )
    event = models.ForeignKey(
        'app.Event',
        on_delete=models.CASCADE,
        related_name='attendees',
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
        return f"{self.id}"

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=[
                    'account',
                    'event',
                ],
                name='unique_attendee',
            )
        ]


class Voter(models.Model):
    id = HashidAutoField(
        primary_key=True,
    )
    ZONE = Choices(
        (1, 'one', 'Zone One'),
        (2, 'two', 'Zone Two'),
        (3, 'three', 'Zone Three'),
        (4, 'four', 'Zone Four'),
        (5, 'five', 'Zone Five'),
    )
    voter_id = models.IntegerField(
        blank=False,
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
    zone = models.IntegerField(
        blank=False,
    )
    address = AddressField(
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    created = models.DateTimeField(
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.ZONE[self.zone]}"


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
    is_verified = models.BooleanField(
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
