import calendar
from calendar import HTMLCalendar
from .models import Wod

WEEK_DAY_DICT = dict(zip(range(7), calendar.day_abbr))


class Calendar(HTMLCalendar):
    def __init__(self):
        super(Calendar, self).__init__()

    def formatday(self, day, weekday, events):
        events_per_day = events.filter(pub_date__day=day)
        d = ''
        for event in events_per_day:
            # d += f'<a href="www.google.de" class="button">{event.strength_type}<br>{event.wod_schema}</a>'
            d += f'{event.get_html_url}'
            # d += f'{event.wod_schema}'

        if day != 0:
            return f"<td class='{WEEK_DAY_DICT[weekday].lower()}'><span class='date'>{day}</span>{d}</td>"
        return '<td></td>'

    def formatweek(self, theweek, events):
        week = ''
        for d, weekday in theweek:
            week += self.formatday(d, weekday, events)
        return f'<tr> {week} </tr>'

    def formatmonth(self, year, month, withyear=True):
        events = Wod.objects.filter(pub_date__year=year, pub_date__month=month)

        cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
        cal += f'{self.formatmonthname(year, month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(year, month):
            cal += f'{self.formatweek(week, events)}\n'
        return cal
