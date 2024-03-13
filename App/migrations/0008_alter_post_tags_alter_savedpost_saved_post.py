# Generated by Django 5.0.1 on 2024-03-13 14:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0007_savedpost'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='tags',
            field=models.ManyToManyField(blank=True, to='App.tag', verbose_name='Post_Tags'),
        ),
        migrations.AlterField(
            model_name='savedpost',
            name='saved_post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App.post'),
        ),
    ]
