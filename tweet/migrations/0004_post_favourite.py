# Generated by Django 3.0.7 on 2020-06-28 07:16

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tweet', '0003_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='favourite',
            field=models.ManyToManyField(related_name='favourite', to=settings.AUTH_USER_MODEL),
        ),
    ]
