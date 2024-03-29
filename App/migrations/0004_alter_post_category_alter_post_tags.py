# Generated by Django 5.0.1 on 2024-03-01 07:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0003_postcategory_post_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='category',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='App.postcategory', verbose_name='Post_Categories'),
        ),
        migrations.AlterField(
            model_name='post',
            name='tags',
            field=models.ManyToManyField(default='', to='App.tag', verbose_name='Post_Tags'),
        ),
    ]
