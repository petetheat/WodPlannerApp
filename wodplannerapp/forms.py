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
    movement_name = forms.ModelChoiceField(queryset=Movement.objects.order_by('movement_name'), initial=0,
                                           label='Übung')


MovementFormSet = forms.formset_factory(MovementForm, extra=1)


class WodMovementForm(forms.Form):
    wod_movement_name = forms.ModelChoiceField(queryset=Movement.objects.order_by('movement_name'), initial=0,
                                               label='Übung')
    # wod_reps = forms.IntegerField(label='Reps', min_value=1, required=False)
    wod_reps = forms.CharField(label='Reps', max_length=20, required=False)
    wod_weight_m = forms.IntegerField(label='Gewicht M', min_value=0, required=False)
    wod_weight_f = forms.IntegerField(label='Gewicht W', min_value=0, required=False)


WodMovementFormSet = forms.formset_factory(WodMovementForm, extra=2)


class RepsForm(forms.Form):
    number_reps = forms.IntegerField(label='Reps', min_value=1, required=True)


RepsFormSet = forms.formset_factory(RepsForm, extra=INITIAL_SET_NUMBER)


class WodFormTime(forms.Form):
    wod_time_rounds = forms.CharField(label='Zeit', max_length=200, initial='20:00')
    wod_comment = forms.CharField(label='Kommentar', max_length=200, required=False)


class WodFormRounds(forms.Form):
    wod_time_rounds = forms.IntegerField(label='Anzahl Runden', initial=3, min_value=1, required=False)
    wod_comment = forms.CharField(label='Kommentar', max_length=200, required=False)


class WodFormTimeRepeat(forms.Form):
    wod_sets = forms.IntegerField(label='Anzahl Runden', initial=3, min_value=1)
    wod_time_rounds = forms.CharField(label='Zeit', max_length=200, initial='5:00')
    wod_comment = forms.CharField(label='Kommentar', max_length=200, required=False)


class StrengthForm(forms.Form):
    # date = forms.DateTimeField(widget=forms.SelectDateWidget(years=YEARS), label='Datum')
    date = forms.DateField(input_formats=['%d/%m/%Y'])
    strength_type = forms.CharField(label='Belastungsart', max_length=5, widget=forms.Select(choices=STRENGTH_CHOICES))
    strength_comment = forms.CharField(label='Kommentar', max_length=100, required=False)
    # strength_sets = forms.IntegerField(label='Sets', initial=INITIAL_SET_NUMBER, min_value=1)


class TrackForm(forms.Form):
    track_type = forms.ModelChoiceField(queryset=Track.objects.order_by('track'), initial=0, label='Track')
