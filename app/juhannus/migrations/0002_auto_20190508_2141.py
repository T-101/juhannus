# Generated by Django 2.2 on 2019-05-08 18:41

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('juhannus', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participant',
            name='vote',
            field=models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(0)]),
        ),
    ]
