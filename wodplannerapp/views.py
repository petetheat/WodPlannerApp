from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from .models import *
from django.http import Http404
from django.urls import reverse
from django.views import generic
from .forms import WodForm, StrengthForm


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
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        # form = WodForm(request.POST)
        form = StrengthForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/wodplannerapp/newwod/')

    # if a GET (or any other method) we'll create a blank form
    else:
        # form = WodForm()
        form = StrengthForm()

    wod_type = schema.schema_name
    # wod_type = schema_key
    print(form)
    return render(request, 'wodplannerapp/definewod.html', {'form_strength': form, 'wod_type': wod_type})
