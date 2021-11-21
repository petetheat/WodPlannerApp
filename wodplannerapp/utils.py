import calendar
from calendar import HTMLCalendar

import pandas as pd
import numpy as np

from .models import Wod, WodMovement, StrengthMovement, Movement
from django.urls import reverse
from collections import Counter

WEEK_DAY_DICT = dict(zip(range(7), calendar.day_abbr))


def _get_wod_dataframe(df_wod, df_movement):
    wod_id = df_wod['wod_id'].unique()[0]
    wod_date = df_wod['wod_dates'].unique()[0]
    df_grouped = df_wod.groupby('wod_movement').wod_id.nunique()
    # df_movement.rename(columns={'movement_name': 'wod_movement'}, inplace=True)
    # df_movement.set_index('wod_movement', inplace=True)

    df_new = df_movement.join(df_grouped)
    df_new.fillna(0, inplace=True)
    df_new.rename(columns={'wod_id': wod_date}, inplace=True)

    return df_new[wod_date]


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
        id_list = [m.wod_id for m in movements]

        movement_list = [m.wod_movement for m in movements]
        strength_movement_list = [m.strength_movement for m in strength_movements]
        list_dates = [wods.filter(id=idx)[0].pub_date for idx in id_list]

        df_dates = pd.DataFrame({'Date': list_dates, 'Movement': movement_list}).sort_values(by=['Movement', 'Date'])
        df_dates.drop_duplicates(subset=['Movement'], keep='last', inplace=True)
        df_dates.sort_values(by='Date', ascending=True, inplace=True)
        df_dates['Date_string'] = df_dates.apply(lambda x: x['Date'].strftime("%d/%m/%Y"), axis=1)

        self.df_dates = df_dates

        move_dict = {m['movement_name']: m['movement_type'] for m in Movement.objects.all().values()}
        movement_type = [move_dict[m] for m in movement_list]

        wod_names = ['WOD%d' % w.id for w in wods]
        wod_ids = [w.id for w in wods]
        dates = [w.pub_date.strftime("%d/%m/%Y") for w in wods]

        df_movement = pd.DataFrame(Movement.objects.all().values())
        df_movement.rename(columns={'movement_name': 'wod_movement'}, inplace=True)
        df_movement.set_index('wod_movement', inplace=True)
        df_wods = pd.DataFrame(movements.values())[['wod_id', 'wod_movement']]
        df_date = pd.DataFrame({'wod_id': wod_ids, 'wod_dates': pd.to_datetime(dates, dayfirst=True)})
        df_wods = df_wods.set_index('wod_id').join(df_date.set_index('wod_id')).reset_index()

        df_list = []
        for wid in wod_ids:
            df_tmp = df_wods.loc[df_wods['wod_id'] == wid]
            df_list.append(_get_wod_dataframe(df_tmp, df_movement))

        self.cm = pd.DataFrame(Counter(movement_list), index=['Anzahl']).T.sort_values(by='Anzahl', ascending=True)
        self.cs = pd.DataFrame(Counter(strength_movement_list), index=['Anzahl']).T.sort_values(by='Anzahl', ascending=True)
        self.mt = pd.DataFrame(Counter(movement_type), index=['Anzahl']).T.sort_values(by='Anzahl', ascending=True)
        # self.mt = pd.DataFrame(mv.values())

        # self.test = pd.DataFrame(np.random.randint(0, 8, (len(movement_list), len(wods))),
        #                          columns=wod_names, index=movement_list).sort_index()
        self.heatmap = pd.concat(df_list, axis=1).sort_index()
        self.heatmap = self.heatmap.T.sort_index().T
        self.heatmap.columns = self.heatmap.columns.strftime('%d-%m-%Y')
