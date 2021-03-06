# Generated by Django 3.2.2 on 2021-05-09 08:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wodplannerapp', '0003_auto_20210508_1959'),
    ]

    operations = [
        migrations.CreateModel(
            name='Wod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pub_date', models.DateTimeField(verbose_name='date published')),
                ('strength_type', models.CharField(max_length=200)),
                ('strength_comment', models.CharField(max_length=200)),
                ('wod_schema', models.CharField(max_length=200)),
                ('wod_time_rounds', models.CharField(max_length=200)),
                ('wod_comment', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='WodMovement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wod_movement', models.CharField(max_length=200)),
                ('wod_reps', models.CharField(max_length=200)),
                ('wod_weight', models.CharField(max_length=200)),
                ('wod', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wodplannerapp.wod')),
            ],
        ),
        migrations.CreateModel(
            name='StrengthMovement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('strength_movement', models.CharField(max_length=200)),
                ('strength_sets_reps', models.CharField(max_length=200)),
                ('wod', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wodplannerapp.wod')),
            ],
        ),
    ]
