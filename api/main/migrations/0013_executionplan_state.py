# Generated by Django 2.1.5 on 2019-03-11 03:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_executionplan_steps_executed'),
    ]

    operations = [
        migrations.AddField(
            model_name='executionplan',
            name='state',
            field=models.CharField(choices=[('new', 'new'), ('finished', 'finished'), ('aborted', 'aborted')], default='new', max_length=24),
        ),
    ]
