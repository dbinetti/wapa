
# Django
from django.contrib import admin

# Local
from .models import Account
from .models import Attendee
from .models import Comment
from .models import School
from .models import Student


class StudentInline(admin.TabularInline):
    model = Student
    fields = [
        'name',
        'account',
        'school',
        'grade',
    ]
    readonly_fields = [
    ]
    ordering = (
    )
    show_change_link = True
    extra = 0
    classes = [
        # 'collapse',
    ]
    autocomplete_fields = [
        'account',
        'school',
    ]


class AttendeeInline(admin.TabularInline):
    model = Attendee
    fields = [
        'account',
        'event',
    ]
    readonly_fields = [
    ]
    ordering = (
    )
    show_change_link = True
    extra = 0
    classes = [
        # 'collapse',
    ]
    autocomplete_fields = [
        'account',
        'event',
    ]

class CommentInline(admin.TabularInline):
    model = Comment
    fields = [
        'account',
        'issue',
        'state',
    ]
    readonly_fields = [
    ]
    ordering = (
    )
    show_change_link = True
    extra = 0
    classes = [
        # 'collapse',
    ]
    autocomplete_fields = [
        'account',
        # 'issue',
    ]


class SchoolInline(admin.TabularInline):
    model = School
    fields = [
        'zone',
        'name',
        'kind',
    ]
    readonly_fields = [
    ]
    ordering = (
    )
    show_change_link = True
    extra = 0
    classes = [
        'collapse',
    ]
    autocomplete_fields = [
        'zone',
        # 'issue',
    ]

class AccountInline(admin.TabularInline):
    model = Account
    fields = [
        'name',
    ]
    readonly_fields = [
    ]
    ordering = (
        'name',
    )
    show_change_link = True
    extra = 0
    classes = [
        'collapse',
    ]
    autocomplete_fields = [
        'zone',
        # 'issue',
    ]
