# Generated by Django 5.0.1 on 2024-02-06 06:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0016_remove_comment_isliked_remove_post_isliked_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commentlike',
            name='comment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App.comment'),
        ),
    ]
