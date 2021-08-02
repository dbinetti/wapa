# Django
from django import forms
from django.contrib.auth.forms import UserChangeForm as UserChangeFormBase
from django.contrib.auth.forms import UserCreationForm as UserCreationFormBase
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

# Local
from .models import Account
from .models import Student
from .models import User
from .models import WrittenComment


class DeleteForm(forms.Form):
    confirm = forms.BooleanField(
        required=True,
    )


class WrittenCommentForm(forms.ModelForm):
    class Meta:
        model = WrittenComment
        fields = [
            'text',
        ]
        widgets = {
            'text': forms.Textarea(
                attrs={
                    'class': 'form-control h-25',
                    'placeholder': 'Comments',
                    'rows': 5,
                }
            ),
        }

    def clean_text(self):
        text= self.cleaned_data['text']
        words = text.split(" ")
        for word in words:
            if any([
                word.startswith("http"),
                word.startswith("www"),
            ]):
                raise ValidationError(
                    "Links are not allowed in comments."
                )
        return text

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


class AccountForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Account
        fields = [
            'name',
            'is_public',
            'address',
            'notes',
        ]
        labels = {
            "is_public": "You May List Me Publicly",
        }
        widgets = {
            'notes': forms.Textarea(
                attrs={
                    'class': 'form-control h-25',
                    'placeholder': 'Anything else we should know? (Optional, Always Private)',
                    'rows': 5,
                }
            )
        }
        help_texts = {
            'name': mark_safe("Please provide your <strong>real full name</strong>, which remains private unless you explcitly choose to be public."),
            'notes': "Any notes to share.",
            'is_public': mark_safe("Making your name public enables <a href='/comments'>Comments</a>."),
            'address': mark_safe("Address always <strong>remains private</strong>; we use this to determine your Board Member."),
        }



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
