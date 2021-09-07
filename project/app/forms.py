# Django
from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AutocompleteSelect
from django.contrib.auth.forms import UserChangeForm as UserChangeFormBase
from django.contrib.auth.forms import UserCreationForm as UserCreationFormBase
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from django.utils.safestring import mark_safe

# Local
from .models import Account
from .models import Attendee
from .models import Comment
from .models import Isat
from .models import Student
from .models import User
from .models import Voter

StudentFormSet = inlineformset_factory(
    Account,
    Student,
    fields=[
        'school',
        'grade',
    ],
    can_delete=True,
    extra=1,
)


class AdminAccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = '__all__'

        widgets = {
            'voter': AutocompleteSelect(
                Account._meta.get_field('voter'),
                admin.site,
                attrs={'style': "width: 400px;"}
            ),
        }


class DeleteForm(forms.Form):
    confirm = forms.BooleanField(
        required=True,
    )

class AttendeeForm(forms.ModelForm):
    class Meta:
        model = Attendee
        fields = [
            'is_confirmed',
            # 'account',
            # 'event',
        ]
        labels = {
            "is_confirmed": "Yes I'll Attend",
        }


class IsatForm(forms.ModelForm):
    class Meta:
        model = Isat
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


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = [
            'content',
        ]
        widgets = {
            'content': forms.Textarea(
                attrs={
                    'class': 'form-control h-25',
                    'placeholder': 'Comments',
                    'rows': 5,
                }
            ),
        }

    def clean_content(self):
        content= self.cleaned_data['content']
        words = content.split(" ")
        for word in words:
            if any([
                word.startswith("http"),
                word.startswith("www"),
            ]):
                raise ValidationError(
                    "Links are not allowed in comments."
                )
        return content

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'name',
            'school',
            'grade',
        ]
        widgets = {
            # 'text': forms.Textarea(
            #     attrs={
            #         'class': 'form-control h-25',
            #         'placeholder': 'Comments',
            #         'rows': 5,
            #     }
            # ),
        }
        help_texts = {
            'name': "Provide first name/initials.",
            'school': "School attending 2021-22.",
            'grade': "Grade for 2021-22.",
        }


class StoryForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = [
            'story',
        ]
        widgets = {
            'story': forms.Textarea(
                attrs={
                    'class': 'form-control h-50',
                    'placeholder': 'Write your story here in your own words.',
                    'rows': 20,
                }
            ),
        }
        help_texts = {
        }


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = [
            'name',
            'is_public',
            'is_spouse',
            'address',
        ]
        labels = {
            "is_public": "I Choose to be Public",
            "is_spouse": "I Represent My Spouse",
        }
        help_texts = {
            'name': mark_safe("Please provide your <strong>real full name</strong>, which remains private unless you explcitly choose to be public."),
            'notes': "Any notes to share.",
            'is_public': mark_safe("Making your name public enables <a href='/comments'>Comments</a>."),
            'is_spouse': "If your spouse shares your position, click here and we'll double your support.",
            'address': mark_safe("We use this to show you're a District Resident (which increases your power.) Your address itself <strong>remains private and confidential</strong>."),
        }

    def clean(self):
        cleaned_data = super().clean()
        is_public = cleaned_data.get("is_public")
        name = cleaned_data.get("name")
        last_name = name.partition(" ")[2]
        full_name = False
        if last_name:
            if len(last_name) > 1 and not last_name.endswith('.'):
                full_name = True
        if is_public and not full_name:
            raise ValidationError(
                "You must provide your full name to be public."
            )


class VoterForm(forms.ModelForm):
    class Meta:
        model = Voter
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


class UserCreationForm(UserCreationFormBase):
    """
    Custom user creation form for Auth0
    """

    # Bypass password requirement
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].required = False
        self.fields['password2'].required = False

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_unusable_password()
        if commit:
            user.save()
        return user

    class Meta:
        model = User
        fields = [
            'username',
        ]


class UserChangeForm(UserChangeFormBase):
    """
    Custom user change form for Auth0
    """

    class Meta:
        model = User
        fields = [
            'username',
        ]
