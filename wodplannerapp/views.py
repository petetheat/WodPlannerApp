from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from .models import *
from django.http import Http404
from django.urls import reverse
from django.views import generic
from .forms import *
from itertools import groupby


def all_equal(iterable):
    g = groupby(iterable)
    return next(g, True) and not next(g, False)


class IndexView(generic.ListView):
    template_name = 'wodplannerapp/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Wod
    template_name = 'wodplannerapp/detail.html'


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'wodplannerapp/results.html'


class CreateWodView(generic.ListView):
    template_name = 'wodplannerapp/createwod.html'
    context_object_name = 'schema_list'

    def get_queryset(self):
        return Schemas.objects.order_by('schema_name')


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


def define_wod(request, schema_key):
    schema = get_object_or_404(Schemas, schema_key=schema_key)

    if request.method == 'POST':
        if schema_key == 'amrap-repeat':
            form = WodFormTimeRepeat(request.POST)
        elif 'amrap' in schema_key or 'emom' in schema_key:
            form = WodFormTime(request.POST)
        else:
            form = WodFormRounds(request.POST)

        form_strength = StrengthForm(request.POST)
        form_strength_movement = MovementFormSet(request.POST, prefix='strengthmove')
        form_reps = RepsFormSet(request.POST, prefix='reps')
        form_wod_movement = WodMovementFormSet(request.POST, prefix='wodmove')

        if form_strength.is_valid() and form.is_valid():
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

            wod = Wod(strength_type=strength_type, pub_date=date, strength_comment=strength_comment,
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

            for f in form_wod_movement:
                print(f.is_valid())
                if f.is_valid():
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
                                                            'form_reps': form_reps})


def success(request):
    return render(request, 'wodplannerapp/success.html')
