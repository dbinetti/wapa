# First-Party
import datetime

from address.models import AddressField
from cloudinary_storage.storage import VideoMediaCloudinaryStorage
from cloudinary_storage.validators import validate_video
from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django_fsm import FSMIntegerField
from django_fsm import transition
from hashid_field import HashidAutoField
from model_utils import Choices
from polymorphic.models import PolymorphicModel

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


class Comment(PolymorphicModel):
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


class WrittenComment(Comment):
    text = models.TextField(
        max_length=2000,
        blank=True,
        default='',
    )

    @property
    def wordcount(self):
        words = self.text.split(" ")
        return len(words)

    class Meta:
        verbose_name = 'Written Comment'
        verbose_name_plural = 'Written Comments'


class VideoComment(Comment):
    video = models.FileField(
        upload_to='videos/',
        blank=True,
        storage=VideoMediaCloudinaryStorage(),
        validators=[validate_video],
    )
    # def __str__(self):
    #     return f"{self.id}"
    class Meta:
        verbose_name = 'Video Comment'
        verbose_name_plural = 'Video Comments'


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
    class Meta:
        ordering = (
            'grade',
        )


    def __str__(self):
        return f"{self.name}"


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
