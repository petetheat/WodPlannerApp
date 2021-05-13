from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from .models import *
from django.http import Http404
from django.urls import reverse
from django.views import generic
from .forms import WodFormTime, WodFormRounds, StrengthForm, MovementFormSet


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
        if 'amrap' in schema_key or 'emom' in schema_key:
            form = WodFormTime(request.POST)
        else:
            form = WodFormRounds(request.POST)
        form_strength = StrengthForm(request.POST)
        form_test = MovementFormSet(request.POST)

        if form_strength.is_valid() and form.is_valid():
            strength_type = form_strength.cleaned_data['strength_type']
            strength_comment = form_strength.cleaned_data['strength_comment']
            date = form_strength.cleaned_data['date']
            wod_time_rounds = form.cleaned_data['wod_time_rounds']
            wod_comment = form.cleaned_data['wod_comment']
            wod = Wod(strength_type=strength_type, pub_date=date, strength_comment=strength_comment,
                      wod_schema=schema.schema_name, wod_time_rounds=wod_time_rounds, wod_comment=wod_comment)
            wod.save()

            for f in form_test:
                if f.is_valid():
                    for k in f.cleaned_data.keys():
                        sm = StrengthMovement(wod=wod, strength_movement=f.cleaned_data[k],
                                              strength_sets_reps='5x5')
                        sm.save()

            # redirect to a new URL:
            return HttpResponseRedirect('/wodplannerapp/success/')

    # if a GET (or any other method) we'll create a blank form
    else:
        if 'amrap' in schema_key or 'emom' in schema_key:
            form = WodFormTime()
        else:
            form = WodFormRounds()
        form_strength = StrengthForm()
        form_strength_movement = MovementFormSet()

    wod_type = schema.schema_name
    # wod_type = schema_key
    return render(request, 'wodplannerapp/definewod.html', {'form_strength': form_strength,
                                                            'form_wod': form, 'wod_type': wod_type,
                                                            'schema_key': schema_key,
                                                            'form_strength_movement': form_strength_movement})


def success(request):
    return render(request, 'wodplannerapp/success.html')
