# Generated by Django 2.1.5 on 2019-02-23 20:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_executionplan'),
    ]

    operations = [
        migrations.AlterField(
            model_name='executionplan',
            name='plan',
            field=models.TextField(null=True),
        ),
    ]
