# Django
from django import forms

# Local
from .models import Voter


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
            'registration',
            'zone',
            'party',
            'gender',
        ]
