# Generated by Django 5.0.1 on 2024-02-23 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0007_alter_bloguser_profileimg'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bloguser',
            name='profileImg',
            field=models.ImageField(default='\\profile.jpg', upload_to='App\\profileimg', verbose_name='Profile Image'),
        ),
    ]
