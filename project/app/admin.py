# Django
# First-Party
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.admin import UserAdmin as UserAdminBase
from django.contrib.gis.admin.options import GISModelAdmin
from django_fsm_log.admin import StateLogInline
from fsm_admin.mixins import FSMTransitionMixin
from reversion.admin import VersionAdmin

# Local
from .forms import AccountAdminForm
from .forms import UserChangeForm
from .forms import UserCreationForm
from .inlines import AccountInline
from .inlines import AttendeeInline
from .inlines import CommentInline
from .inlines import SchoolInline
from .inlines import StudentInline
from .models import Account
from .models import Comment
from .models import Event
from .models import Isat
from .models import Issue
from .models import School
from .models import Staff
from .models import User
from .models import Zone


def approve(modeladmin, request, queryset):
    for comment in queryset:
        comment.approve()
        comment.save()
approve.short_description = 'Approve Comment'


@admin.register(Account)
class AccountAdmin(VersionAdmin, GISModelAdmin):
    def get_changelist_form(self, request, **kwargs):
        return AccountAdminForm

    form = AccountAdminForm
    save_on_top = True
    fields = [
        'picture',
        'name',
        'address',
        'geocode',
        'is_precise',
        'place',
        'point',
        'is_public',
        'is_spouse',
        'zone',
        'user',
        # 'notes',
    ]
    list_display = [
        'id',
        'name',
        'address',
        # 'is_public',
        # 'is_spouse',
        # 'zone',
        # 'notes',
    ]
    list_editable = [
        'name',
        'address',
    ]
    list_per_page = 10
    list_filter = [
        'is_public',
        'is_precise',
        'is_spouse',
        'zone',
    ]
    search_fields = [
        'name',
        'user__email',
    ]
    autocomplete_fields = [
        'user',
    ]
    inlines = [
        StudentInline,
        CommentInline,
    ]
    ordering = [
        '-created',
    ]
    # formfield_overrides = {
    #     AddressField: {
    #         'widget': AddressWidget(
    #             attrs={'style': "width: 600px;"}
    #         )
    #     },
    # }
    readonly_fields = [
        # 'place',
    ]


@admin.register(Comment)
class CommentAdmin(FSMTransitionMixin, VersionAdmin):
    save_on_top = True
    search_fields = [
        'account__name',
    ]
    fields = [
        'state',
        'is_featured',
        'issue',
        'content',
    ]
    fsm_fields = [
        'state',
    ]
    list_filter = [
        'state',
        'is_featured',
        'issue',
    ]
    list_display = [
        '__str__',
        'state',
        'issue',
        'content',
    ]
    ordering = [
        '-created',
    ]
    autocomplete_fields = [
        'account',
        # 'issue',
    ]
    list_select_related = [
        'account',
        'issue',
    ]
    actions = [
        approve,
    ]
    inlines = [
        StateLogInline,
    ]


@admin.register(Staff)
class StaffAdmin(VersionAdmin):
    save_on_top = True
    fields = [
        'name',
        'position',
        'school_raw',
        'school',
    ]
    list_filter = [
    ]
    list_display = [
        'name',
        'position',
        'school_raw',
        'school',
    ]
    ordering = [
        '-created',
    ]
    autocomplete_fields = [
        'school',
        # 'issue',
    ]
    list_select_related = [
        'school',
    ]


@admin.register(Event)
class EventAdmin(VersionAdmin):
    save_on_top = True
    fields = [
        'name',
        'datetime',
        'description',
        'location',
        'notes',
    ]
    list_display = [
        'name',
        'datetime',
        'location',
    ]
    list_editable = [
    ]
    list_filter = [
        'datetime',
    ]
    search_fields = [
        'name',
    ]
    inlines = [
        AttendeeInline,
    ]
    autocomplete_fields = [
    ]


@admin.register(Isat)
class IsatAdmin(VersionAdmin):
    save_on_top = True
    fields = [
        'subject',
        'grade',
        'year',
        'advanced_note',
        'proficient_note',
        'basic_note',
        'below_note',
        'advanced',
        'proficient',
        'basic',
        'below',
        'school',
    ]
    list_display = [
        'id',
        'subject',
        'grade',
        'year',
        'advanced_note',
        'proficient_note',
        'basic_note',
        'below_note',
        'advanced',
        'proficient',
        'basic',
        'below',
        'school',
    ]
    list_editable = [
    ]
    list_filter = [
        'subject',
        'grade',
        'school',
        'year',
    ]
    search_fields = [
    ]
    inlines = [
    ]
    ordering = [
    ]


@admin.register(Issue)
class IssueAdmin(VersionAdmin):
    save_on_top = True
    fields = [
        'name',
        'date',
        'state',
        'description',
        'recipient_name',
        'recipient_emails',
    ]
    list_display = [
        'name',
        'date',
    ]
    list_editable = [
    ]
    list_filter = [
    ]
    search_fields = [
        'name',
        'date',
    ]
    inlines = [
        # CommentInline,
    ]
    autocomplete_fields = [
    ]


@admin.register(School)
class SchoolAdmin(VersionAdmin, GISModelAdmin):
    save_on_top = True
    fields = (
        'name',
        'full',
        'kind', (
            'enrollment',
            'size',
            'capacity',
        ),
        'location_id',
        'gis_id',
        'school_id',
        'point',
        'address_raw',
        'phone_raw',
        'zone',
        # 'poly',
    )
    list_display = [
        'id',
        'name',
        'gis_id',
        # 'full',
        # 'school_id',
        # 'kind',
    ]
    list_editable = [
        'name',
        'gis_id',

        # 'full',
        # 'kind',
        # 'school_id',
    ]
    list_filter = [
        'kind',
    ]
    search_fields = [
        'name',
    ]
    ordering = [
        'kind',
        'name',
        '-created',
    ]


@admin.register(Zone)
class ZoneAdmin(VersionAdmin, GISModelAdmin):
    save_on_top = True
    fields = [
        'name',
        'trustee_name',
        'trustee_email',
        'poly',
    ]
    list_display = [
        'name',
        'trustee_name',
        'trustee_email',
    ]
    list_editable = [
    ]
    list_filter = [
        'name',
    ]
    search_fields = [
        'name',
        'trustee_name',
        'trustee_email',
    ]
    inlines = [
        SchoolInline,
        # AccountInline,
    ]
    autocomplete_fields = [
    ]
    ordering = [
        'name',
    ]


@admin.register(User)
class UserAdmin(UserAdminBase):
    save_on_top = True
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    fieldsets = (
        (None, {
            'fields': [
                'username',
            ]
        }
        ),
        ('Data', {
            'fields': [
                'name',
                'email',
                'is_verified',
            ]
        }
        ),
        ('Permissions', {'fields': ('is_admin', 'is_active')}),
    )
    list_display = [
        # 'username',
        'name',
        'email',
        'is_verified',
        'created',
        'last_login'
    ]
    list_filter = [
        'is_active',
        'is_admin',
        'is_verified',
        'created',
        'last_login',
    ]
    search_fields = [
        'username',
        'name',
        'email',
    ]
    ordering = [
        '-created',
    ]
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': [
                'username',
                'is_admin',
                'is_active',
                'is_verified',
            ]
        }
        ),
    )
    filter_horizontal = ()
    inlines = [
    ]
    readonly_fields = [
        'name',
        'email',
    ]


# Use Auth0 for login
admin.site.login = staff_member_required(
    admin.site.login,
    login_url=settings.LOGIN_URL,
)
