# Django
# First-Party
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.admin import UserAdmin as UserAdminBase
from fsm_admin.mixins import FSMTransitionMixin
from reversion.admin import VersionAdmin

# Local
from .forms import UserChangeForm
from .forms import UserCreationForm
from .inlines import AttendeeInline
from .inlines import CommentInline
from .inlines import StudentInline
from .models import Account
from .models import Comment
from .models import Event
from .models import Isat
from .models import Issue
from .models import School
from .models import User
from .models import Voter


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


@admin.register(Voter)
class VoterAdmin(VersionAdmin):
    save_on_top = True
    fields = [
        'voter_id',
        'last_name',
        'first_name',
        'middle_name',
        'suffix',
        'age',
        'street',
        'city',
        'st',
        'zipcode',
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
    ]
    search_fields = [
        'first_name',
        'last_name',
    ]
    inlines = [
    ]
    ordering = [
        'last_name',
        'first_name',
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


def approve(modeladmin, request, queryset):
    for comment in queryset:
        comment.approve()
        comment.save()
approve.short_description = 'Approve Comment'


@admin.register(Account)
class AccountAdmin(VersionAdmin):
    save_on_top = True
    fields = [
        'name',
        'picture',
        'address',
        'is_public',
        'is_spouse',
        'is_steering',
        'zone',
        # 'notes',
    ]
    list_display = [
        'name',
        'address',
        'is_public',
        'is_spouse',
        'is_steering',
        'zone',
        # 'notes',
    ]
    list_editable = [
    ]
    list_filter = [
        'is_public',
        'is_steering',
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
class SchoolAdmin(VersionAdmin):
    save_on_top = True
    fields = [
        'name',
        'full',
        'kind',
        'school_id',
    ]
    list_display = [
        'id',
        'name',
        'full',
        'school_id',
        'kind',
    ]
    list_editable = [
        'name',
        'full',
        'kind',
        'school_id',
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

@admin.register(Comment)
class CommentAdmin(FSMTransitionMixin, VersionAdmin):
    save_on_top = True
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
        # 'issue',
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
