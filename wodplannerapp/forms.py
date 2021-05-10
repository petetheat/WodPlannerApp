from django import forms
from .models import *

# STRENGTH_CHOICES = ['Lower', 'Upper', 'Skill', 'Oly']
STRENGTH_CHOICES = [
    ('LOWER', 'Lower'),
    ('UPPER', 'Upper'),
    ('SKILL', 'Skill'),
    ('OLY', 'Oly')
]


class WodForm(forms.Form):
    strength_movement = forms.CharField(label='Strength Movement', max_length=100)
    strength_comment = forms.CharField(label='Strength Comment', max_length=100)


class StrengthForm(forms.Form):

    strength_type = forms.CharField(label='Strength Type', max_length=5, widget=forms.Select(choices=STRENGTH_CHOICES))
    # strength_movement = forms.CharField(label='Strength Movement', max_length=100)
    strength_movement = forms.ModelChoiceField(queryset=Movement.objects.all(), initial=0)
    strength_comment = forms.CharField(label='Strength Comment', max_length=100)

