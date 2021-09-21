# Django
# First-Party
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.admin import UserAdmin as UserAdminBase
from fsm_admin.mixins import FSMTransitionMixin
from reversion.admin import VersionAdmin

# Local
from .models import Voter


@admin.register(Voter)
class VoterAdmin(VersionAdmin):
    save_on_top = True
    fields = [
        'voter_id',
        'name',
        'address',
        'point',
        'place',
        'geocode',
        'is_precise',
        'last_name',
        'first_name',
        'middle_name',
        'suffix',
        'age',
        'street',
        'city',
        'st',
        'zipcode',
        'gender',
        'party',
        'registration',
        'zone',
    ]
    list_display = [
        'last_name',
        'first_name',
        'age',
        'zone',
    ]
    list_editable = [
    ]
    list_filter = [
        'zone',
        'is_precise',
    ]
    inlines = [
    ]
    ordering = [
        'last_name',
        'first_name',
    ]
    search_fields = [
        'last_name',
        'first_name',
        'street',
        'city',
        'st',
        'zipcode',
    ]
    readonly_fields = [
        'name',
        'address',
        'point',
        'place',
        'geocode',
    ]
