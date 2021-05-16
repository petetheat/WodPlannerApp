import datetime

from django.db import models
from django.utils import timezone
from django.urls import reverse


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text


class Movement(models.Model):
    movement_name = models.CharField(max_length=200)
    movement_type = models.CharField(max_length=200)

    def __str__(self):
        return self.movement_name


class Schemas(models.Model):
    schema_name = models.CharField(max_length=200)
    schema_description = models.CharField(max_length=200)
    schema_key = models.CharField(max_length=200)

    def __str__(self):
        return self.schema_name


class Wod(models.Model):
    pub_date = models.DateTimeField('date published')
    strength_type = models.CharField(max_length=200)
    strength_comment = models.CharField(max_length=200)
    wod_schema = models.CharField(max_length=200)
    wod_time_rounds = models.CharField(max_length=200)
    wod_comment = models.CharField(max_length=200)

    def __str__(self):
        return 'WOD%d' % self.id

    @property
    def get_html_url(self):
        url = reverse('wodplannerapp:detail', args=(self.id,))
        return f'<a href="{url}" class="button-calendar"> {self.strength_type}<br>{self.wod_schema} </a>'


class StrengthMovement(models.Model):
    wod = models.ForeignKey(Wod,  on_delete=models.CASCADE)
    strength_movement = models.CharField(max_length=200)
    strength_sets_reps = models.CharField(max_length=200)

    def __str__(self):
        return self.strength_movement


class WodMovement(models.Model):
    wod = models.ForeignKey(Wod, on_delete=models.CASCADE)
    wod_movement = models.CharField(max_length=200)
    wod_reps = models.CharField(max_length=200)
    wod_weight = models.CharField(max_length=200)

    def __str__(self):
        return self.wod_movement
