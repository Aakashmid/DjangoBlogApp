# Generated by Django 5.0.1 on 2024-04-06 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0009_post_thimg'),
    ]

    operations = [
        migrations.AddField(
            model_name='bloguser',
            name='likedPosts',
            field=models.JSONField(default={}),
        ),
        migrations.AddField(
            model_name='bloguser',
            name='savedPosts',
            field=models.JSONField(default={}),
        ),
    ]