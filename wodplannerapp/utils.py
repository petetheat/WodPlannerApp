import calendar
from calendar import HTMLCalendar

import pandas as pd

from .models import Wod, WodMovement, StrengthMovement, Movement
from django.urls import reverse
from collections import Counter

WEEK_DAY_DICT = dict(zip(range(7), calendar.day_abbr))


class Calendar(HTMLCalendar):
    def __init__(self):
        super(Calendar, self).__init__()

    def formatday(self, year, month, day, weekday, events):
        events_per_day = events.filter(pub_date__day=day)
        d = ''
        if len(events_per_day) > 0:
            # for event in events_per_day:
            # d += f'<a href="www.google.de" class="button">{event.strength_type}<br>{event.wod_schema}</a>'
            # d += f'{event.get_html_url}'
            # d += f'{event.wod_schema}'
            url = reverse('wodplannerapp:dayview', args=(year, month, day))
            d += f'<a href="{url}" class="button-calendar"> WODs </a>'

        if day != 0:
            return f"<td class='{WEEK_DAY_DICT[weekday].lower()}'><span class='date'>{day}</span><br>{d}</td>"
        return '<td class="empty-day"></td>'

    def formatweek(self, year, month, theweek, events):
        week = ''
        for d, weekday in theweek:
            week += self.formatday(year, month, d, weekday, events)
        return f'<tr class="cal-week"> {week} </tr>'

    def formatmonth(self, year, month, withyear=True):
        events = Wod.objects.filter(pub_date__year=year, pub_date__month=month)

        cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
        cal += f'{self.formatmonthname(year, month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(year, month):
            cal += f'{self.formatweek(year, month, week, events)}\n'
        return cal


class AnalyzeWods:
    def __init__(self, track_id):
        wods = Wod.objects.filter(track=track_id)
        movements = WodMovement.objects.filter(wod_id__in=[w.id for w in wods])
        strength_movements = StrengthMovement.objects.filter(wod_id__in=[w.id for w in wods])

        movement_list = [m.wod_movement for m in movements]
        strength_movement_list = [m.strength_movement for m in strength_movements]

        move_dict = {m['movement_name']: m['movement_type'] for m in Movement.objects.all().values()}
        movement_type = [move_dict[m] for m in movement_list]

        self.cm = pd.DataFrame(Counter(movement_list), index=['Anzahl']).T.sort_values(by='Anzahl', ascending=True)
        self.cs = pd.DataFrame(Counter(strength_movement_list), index=['Anzahl']).T.sort_values(by='Anzahl', ascending=True)
        self.mt = pd.DataFrame(Counter(movement_type), index=['Anzahl']).T.sort_values(by='Anzahl', ascending=True)
        # self.mt = pd.DataFrame(mv.values())

