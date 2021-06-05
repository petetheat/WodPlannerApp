from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from .models import *
from django.http import Http404
from django.urls import reverse
from django.views import generic
from .forms import *
from itertools import groupby

from plotly.offline import plot
from plotly.graph_objs import Scatter, Bar, Layout
import plotly.express as px
import pandas as pd

import datetime
import calendar
from .utils import Calendar, AnalyzeWods

from django.contrib.auth.decorators import login_required


pd.options.plotting.backend = "plotly"


def all_equal(iterable):
    g = groupby(iterable)
    return next(g, True) and not next(g, False)


def previous_month(t):
    t_prev = t.replace(day=1) - datetime.timedelta(days=1)
    return t_prev.year, t_prev.month


def next_month(t):
    last_day = calendar.monthrange(t.year, t.month)[-1]
    t_next = t.replace(day=last_day) + datetime.timedelta(days=1)
    return t_next.year, t_next.month


@login_required
def index_view(request):
    username = None
    if request.user.is_authenticated:
        username = request.user.username
    t_now = datetime.datetime.now()
    year = t_now.year
    month = t_now.month
    template_name = 'wodplannerapp/index.html'

    return render(request, template_name, {'year': year, 'month': month, 'user': username})


@login_required
def detail_view(request, wod_id):
    wod = get_object_or_404(Wod, pk=wod_id)

    t_now = datetime.datetime.now()
    year = t_now.year
    month = t_now.month
    day = t_now.day

    context_dict = {'wod': wod, 'year': year, 'month': month, 'day': day}
    template_name = 'wodplannerapp/detail.html'

    return render(request, template_name, context_dict)


# @login_required
class ResultsView(generic.DetailView):
    model = Question
    template_name = 'wodplannerapp/results.html'


# @login_required
class CreateWodView(generic.ListView):
    template_name = 'wodplannerapp/createwod.html'
    context_object_name = 'schema_list'

    def get_queryset(self):
        return Schemas.objects.order_by('schema_name')


# @login_required
class WodOverview(generic.ListView):
    template_name = 'wodplannerapp/wodoverview.html'
    context_object_name = 'wod_list'

    def get_queryset(self):
        return Wod.objects.order_by('pub_date')


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'wodplannerapp/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('wodplannerapp:results', args=(question.id,)))


@login_required
def define_wod(request, schema_key):
    schema = get_object_or_404(Schemas, schema_key=schema_key)

    if request.method == 'POST':
        if schema_key == 'amrap-repeat':
            form = WodFormTimeRepeat(request.POST)
        elif 'amrap' in schema_key or 'emom' in schema_key:
            form = WodFormTime(request.POST)
        else:
            form = WodFormRounds(request.POST)

        form_track = TrackForm(request.POST)
        form_strength = StrengthForm(request.POST)
        form_strength_movement = MovementFormSet(request.POST, prefix='strengthmove')
        form_reps = RepsFormSet(request.POST, prefix='reps')
        form_wod_movement = WodMovementFormSet(request.POST, prefix='wodmove', initial=[{'wod_weight_m': '20',
                                                                                         'wod_weight_f': '16'},
                                                                                        {'wod_weight_m': '20',
                                                                                         'wod_weight_f': '16'}])

        if form_strength.is_valid() and form.is_valid() and form_track.is_valid():
            track_type = form_track.cleaned_data['track_type']
            track = Track.objects.get(track=track_type)

            strength_type = form_strength.cleaned_data['strength_type']
            strength_comment = form_strength.cleaned_data['strength_comment']
            date = form_strength.cleaned_data['date']

            if schema_key != 'amrap-repeat':
                wod_time_rounds = form.cleaned_data['wod_time_rounds'] if form.cleaned_data['wod_time_rounds'] is not None else ''
            else:
                n_rounds = form.cleaned_data['wod_sets']
                n_time = form.cleaned_data['wod_time_rounds']
                wod_time_rounds = '%sx%s' % (n_rounds, n_time)
            wod_comment = form.cleaned_data['wod_comment']

            wod = Wod(track=track, strength_type=strength_type, pub_date=date, strength_comment=strength_comment,
                      wod_schema=schema.schema_name, wod_time_rounds=wod_time_rounds, wod_comment=wod_comment)
            wod.save()

            set_reps = []
            for f in form_reps:
                if f.is_valid():
                    for k in f.cleaned_data.keys():
                        set_reps.append(f.cleaned_data[k])

            if all_equal(set_reps) and len(set_reps) > 0:
                strength_sets_reps = '%dx%d' % (len(set_reps), set_reps[0])
            elif not all_equal(set_reps):
                strength_sets_reps = '-'.join(str(x) for x in set_reps)
            else:
                strength_sets_reps = '%dx[..]' % len(form_reps)

            for f in form_strength_movement:
                if f.is_valid():
                    for k in f.cleaned_data.keys():
                        sm = StrengthMovement(wod=wod, strength_movement=f.cleaned_data[k],
                                              strength_sets_reps=strength_sets_reps)
                        sm.save()

            print(len(form_wod_movement))
            for f in form_wod_movement:
                if f.is_valid():
                    print(f.cleaned_data.keys())
                    if f.cleaned_data['wod_reps'] is None:
                        wod_reps = ''
                    else:
                        wod_reps = f.cleaned_data['wod_reps']

                    if f.cleaned_data['wod_weight_m'] is None:
                        w_m = ''
                    else:
                        w_m = f.cleaned_data['wod_weight_m']

                    if f.cleaned_data['wod_weight_f'] is None:
                        w_f = ''
                    else:
                        w_f = f.cleaned_data['wod_weight_f']

                    if w_m == '' and w_f == '':
                        weight = ''
                    else:
                        weight = '%skg/%skg' % (w_m, w_f)

                    wm = WodMovement(wod=wod, wod_movement=f.cleaned_data['wod_movement_name'],
                                     wod_reps=wod_reps, wod_weight=weight)
                    wm.save()
                else:
                    print(f.errors)
            # redirect to a new URL:
            return HttpResponseRedirect('/wodplannerapp/success/')

    # if a GET (or any other method) we'll create a blank form
    else:
        if schema_key == 'amrap-repeat':
            form = WodFormTimeRepeat()
        elif 'amrap' in schema_key or 'emom' in schema_key:
            form = WodFormTime()
        else:
            form = WodFormRounds()

        form_track = TrackForm()
        form_strength = StrengthForm()
        form_strength_movement = MovementFormSet(prefix='strengthmove')
        form_reps = RepsFormSet(prefix='reps')
        form_wod_movement = WodMovementFormSet(prefix='wodmove')

    wod_type = schema.schema_name

    return render(request, 'wodplannerapp/definewod.html', {'form_strength': form_strength,
                                                            'form_wod': form, 'wod_type': wod_type,
                                                            'form_wod_movement': form_wod_movement,
                                                            'schema_key': schema_key,
                                                            'form_strength_movement': form_strength_movement,
                                                            'form_reps': form_reps,
                                                            'form_track': form_track})


@login_required
def success(request):
    return render(request, 'wodplannerapp/success.html')


@login_required
def calendar_view(request, year, month):
    mycalendar = Calendar()
    t = datetime.datetime(year, month, 1, 0, 0, 0, 0)
    year_next, month_next = next_month(t)
    year_prev, month_prev = previous_month(t)

    context_dict = {'year': year, 'month': month,
                    'year_next': year_next, 'month_next': month_next,
                    'year_prev': year_prev, 'month_prev': month_prev,
                    'calendar': mycalendar.formatmonth(year, month)}
    return render(request, 'wodplannerapp/calendar.html', context_dict)


@login_required
def day_view(request, year, month, day):
    wods = Wod.objects.filter(pub_date__year=year, pub_date__month=month, pub_date__day=day)

    context_dict = {'wods': wods}
    return render(request, 'wodplannerapp/dayview.html', context_dict)


@login_required
def getmovements(request):

    if 'term' in request.GET:
        qs = Movement.objects.filter(movement_name__icontains=request.GET.get('term'))
        movement_list = []
        for m in qs:
            movement_list.append(m.movement_name)
        return JsonResponse(movement_list, safe=False)


class AnalysisOverView(generic.ListView):
    template_name = 'wodplannerapp/analysisoverview.html'
    context_object_name = 'track_list'

    def get_queryset(self):
        return Track.objects.all()


@login_required
def analysis(request, track_id):
    template_name = 'wodplannerapp/analysis.html'

    wod_analyzer = AnalyzeWods(track_id)

    # plot_div = plot([Bar(x=list(wod_analyzer.cm.values()), y=list(wod_analyzer.cm.keys()),
    #                      orientation='h')],
    #                 output_type='div',
    #                 include_plotlyjs=False)

    layout = Layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    y_ax = dict(showgrid=False, color='#aaa')
    x_ax = dict(showgrid=False, color='#aaa', scaleanchor='x')

    fig = wod_analyzer.cm.plot.barh()
    fig.update_layout(title_font_size=30, paper_bgcolor='rgba(200,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)', yaxis=y_ax, xaxis=x_ax, showlegend=False,
                      xaxis_title="Anzahl",
                      yaxis_title="Bewegung")
    fig.update_traces(marker_color='green')
    fig.update_xaxes(fixedrange=True)
    plot_div1 = plot(fig, output_type='div', include_plotlyjs=False)

    fig2 = wod_analyzer.cs.plot.barh()
    fig2.update_layout(title_font_size=30, paper_bgcolor='rgba(200,0,0,0)',
                       plot_bgcolor='rgba(0,0,0,0)', yaxis=y_ax, xaxis=x_ax, showlegend=False,
                       xaxis_title="Anzahl",
                       yaxis_title="Bewegung")
    fig2.update_traces(marker_color='green')
    fig2.update_xaxes(fixedrange=True)
    plot_div2 = plot(fig2, output_type='div', include_plotlyjs=False)

    fig = px.bar(wod_analyzer.mt,
                 x=[c for c in wod_analyzer.mt.columns],
                 y=wod_analyzer.mt.index)
    fig.update_layout(title_font_size=30, paper_bgcolor='rgba(200,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)', yaxis=y_ax, xaxis=x_ax, showlegend=False,
                      xaxis_title="Anzahl",
                      yaxis_title="Bewegungsart")
    fig.update_traces(marker_color='green')
    fig.update_layout(barmode='stack')
    plot_div3 = plot(fig, output_type='div', include_plotlyjs=False)

    fig = px.imshow(wod_analyzer.heatmap)
    fig.update_layout(title_font_size=30, paper_bgcolor='rgba(200,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)', yaxis=y_ax, xaxis=x_ax, showlegend=False,
                      xaxis_title="Workouts",
                      yaxis_title="Bewegungen",
                      margin=dict(l=5, r=5, t=5, b=5))
    fig.update_traces(dict(showscale=False,
                           coloraxis=None), selector={'type': 'heatmap'})
    fig.update_xaxes(fixedrange=True)
    # fig.update_yaxes(fixedrange=True)
    print(fig)
    plot_div4 = plot(fig, output_type='div', include_plotlyjs=False)

    context_dict = {'plot_div': plot_div1,
                    'plot_div_s': plot_div2,
                    'plot_div_mt': plot_div3,
                    'plot_div_test': plot_div4}

    return render(request, template_name, context_dict)
