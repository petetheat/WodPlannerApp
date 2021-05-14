from django import forms
from .models import *

# STRENGTH_CHOICES = ['Lower', 'Upper', 'Skill', 'Oly']
STRENGTH_CHOICES = [
    ('Lower', 'Lower'),
    ('Upper', 'Upper'),
    ('Skill', 'Skill'),
    ('Oly', 'Oly'),
    ('Core', 'Core')
]
YEARS = [str(x) for x in range(2020, 2031, 1)]
INITIAL_SET_NUMBER = 5


class MovementForm(forms.Form):
    movement_name = forms.ModelChoiceField(queryset=Movement.objects.all(), initial=0, label='Übung')


MovementFormSet = forms.formset_factory(MovementForm, extra=1)


class RepsForm(forms.Form):
    number_reps = forms.IntegerField(label='Reps', min_value=1, required=True)


RepsFormSet = forms.formset_factory(RepsForm, extra=INITIAL_SET_NUMBER)


class WodFormTime(forms.Form):
    wod_time_rounds = forms.CharField(label='Zeit', max_length=200, initial='20:00')
    wod_comment = forms.CharField(label='Kommentar', max_length=200, required=False)


class WodFormRounds(forms.Form):
    wod_time_rounds = forms.IntegerField(label='Anzahl Runden', initial=3, min_value=1)
    wod_comment = forms.CharField(label='Kommentar', max_length=200, required=False)


class StrengthForm(forms.Form):
    date = forms.DateField(widget=forms.SelectDateWidget(years=YEARS), label='Datum')
    strength_type = forms.CharField(label='Belastungsart', max_length=5, widget=forms.Select(choices=STRENGTH_CHOICES))
    strength_comment = forms.CharField(label='Kommentar', max_length=100, required=False)
    strength_sets = forms.IntegerField(label='Sets', initial=INITIAL_SET_NUMBER, min_value=1)
