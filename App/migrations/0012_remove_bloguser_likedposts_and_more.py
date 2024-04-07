# Generated by Django 5.0.1 on 2024-04-06 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0011_alter_bloguser_likedposts_alter_bloguser_savedposts'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bloguser',
            name='likedPosts',
        ),
        migrations.RemoveField(
            model_name='bloguser',
            name='savedPosts',
        ),
        migrations.AddField(
            model_name='bloguser',
            name='session_data',
            field=models.JSONField(default=dict),
        ),
    ]
