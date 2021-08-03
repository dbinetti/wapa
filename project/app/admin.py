# Django
# First-Party
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.admin import UserAdmin as UserAdminBase
from fsm_admin.mixins import FSMTransitionMixin
from polymorphic.admin import PolymorphicChildModelAdmin
from polymorphic.admin import PolymorphicChildModelFilter
from polymorphic.admin import PolymorphicParentModelAdmin
from reversion.admin import VersionAdmin

# Local
from .forms import UserChangeForm
from .forms import UserCreationForm
from .inlines import CommentInline
from .inlines import StudentInline
from .models import Account
from .models import Comment
from .models import Issue
from .models import School
from .models import User
from .models import VideoComment
from .models import WrittenComment


@admin.register(Account)
class AccountAdmin(VersionAdmin):
    save_on_top = True
    fields = [
        'name',
        'address',
        'is_public',
        'is_steering',
        # 'notes',
    ]
    list_display = [
        'name',
        'address',
        'is_public',
        'is_steering',
        # 'notes',
    ]
    list_editable = [
    ]
    list_filter = [
        'is_public',
        'is_steering',
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
        'description',
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
        CommentInline,
    ]
    autocomplete_fields = [
    ]

@admin.register(School)
class SchoolAdmin(VersionAdmin):
    save_on_top = True
    fields = [
        'name',
    ]
    list_display = [
        'name',
    ]
    list_editable = [
    ]
    list_filter = [
    ]
    search_fields = [
        'name',
    ]
    ordering = [
        '-created',
    ]

@admin.register(Comment)
class CommentAdmin(FSMTransitionMixin, PolymorphicParentModelAdmin, VersionAdmin):
    save_on_top = True
    fields = [
        # 'video',
        'state',
        'is_featured',
        'issue',
    ]
    fsm_fields = [
        'state',
    ]
    list_filter = [
        'state',
        'is_featured',
        PolymorphicChildModelFilter,
        'issue',
    ]
    list_display = [
        '__str__',
        'state',
        'issue',
    ]
    ordering = [
        '-created',
    ]
    child_models = [
        WrittenComment,
        VideoComment,
    ]
    autocomplete_fields = [
        'account',
        # 'issue',
    ]
    list_select_related = [
        'account',
        'issue',
    ]


@admin.register(WrittenComment)
class WrittenCommentAdmin(FSMTransitionMixin, PolymorphicChildModelAdmin, VersionAdmin):
    save_on_top = True
    fsm_fields = [
        'state',
    ]
    fields = [
        'state',
        'is_featured',
        'account',
        'issue',
        'text',
    ]
    list_display = [
        'text',
    ]
    ordering = [
        '-created',
    ]
    autocomplete_fields = [
        'account',
        # 'issue',
    ]
    base_model = Comment


@admin.register(VideoComment)
class VideoCommentAdmin(FSMTransitionMixin, PolymorphicChildModelAdmin, VersionAdmin):
    save_on_top = True
    fields = [
        'state',
        'is_featured',
        'account',
        'issue',
        'video',
    ]
    list_display = [
        'account',
        'state',
        'video',
    ]
    list_filter = [
        'state',
    ]
    ordering = [
        '-created',
    ]
    autocomplete_fields = [
        'account',
        # 'issue',
    ]
    base_model = Comment


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
            ]
        }
        ),
        ('Permissions', {'fields': ('is_admin', 'is_active')}),
    )
    list_display = [
        # 'username',
        'name',
        'email',
        'created',
        'last_login'
    ]
    list_filter = [
        'is_active',
        'is_admin',
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
