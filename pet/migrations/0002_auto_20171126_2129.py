# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-26 14:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pet', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchase',
            name='subscribers',
            field=models.ManyToManyField(blank=True, related_name='subscribed_purchases', to='pet.UserProfile'),
        ),
    ]
