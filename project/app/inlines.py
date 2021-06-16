
# Django
from django.contrib import admin

# Local
from .models import Student


class StudentInline(admin.TabularInline):
    model = Student
    fields = [
        'name',
        'account',
        'school',
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
