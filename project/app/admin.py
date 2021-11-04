# Django
# First-Party
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.admin import UserAdmin as UserAdminBase
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
from .models import User
from .models import Zone
from .widgets import AddressWidget


def approve(modeladmin, request, queryset):
    for comment in queryset:
        comment.approve()
        comment.save()
approve.short_description = 'Approve Comment'


class AddressFilter(admin.SimpleListFilter):
    title = ('Is Address')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'is_address'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('is_address', ('Is Address')),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == 'is_address':
            return queryset.filter(
                point__isnull=True,
            ).exclude(
                address_too='',
            )

@admin.register(Account)
class AccountAdmin(VersionAdmin):
    def get_changelist_form(self, request, **kwargs):
        return AccountAdminForm

    form = AccountAdminForm
    save_on_top = True
    fields = [
        'picture',
        'name',
        'address_too',
        'address_raw',
        # 'voter',
        # 'point',
        # 'is_influential',
        'geocode',
        'is_precise',
        'place',
        'point',
        'is_public',
        'is_spouse',
        'is_steering',
        'is_vip',
        'zone',
        'user',
        # 'notes',
    ]
    list_display = [
        'id',
        'name',
        'address_too',
        'address_raw',
        'is_vip',
        # 'is_public',
        # 'is_spouse',
        # 'is_steering',
        # 'zone',
        # 'notes',
    ]
    list_editable = [
        'name',
        'address_too',
    ]
    list_per_page = 10
    list_filter = [
        AddressFilter,
        'is_public',
        'is_steering',
        'is_precise',
        'is_spouse',
        'zone',
        'is_vip',
    ]
    search_fields = [
        'name',
        'user__email',
    ]
    autocomplete_fields = [
        'user',
        # 'voter',
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


@admin.register(Zone)
class ZoneAdmin(VersionAdmin):
    save_on_top = True
    fields = [
        'name',
        'trustee_name',
        'trustee_email',
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
        AccountInline,
    ]
    autocomplete_fields = [
    ]
    ordering = [
        'name',
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
        'nurse_name',
        'nurse_email',
        'full',
        'kind',
        'school_id',
        'point',
        'address_raw',
        'phone_raw',
        'zone',
    ]
    list_display = [
        'id',
        'name',
        'nurse_name',
        'nurse_email',
        # 'full',
        # 'school_id',
        # 'kind',
        # 'address_raw'
    ]
    list_editable = [
        'name',
        'nurse_name',
        'nurse_email',
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
