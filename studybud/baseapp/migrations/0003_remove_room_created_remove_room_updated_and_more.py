# Generated by Django 4.2.14 on 2024-07-28 22:20

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('baseapp', '0002_topic_room_host_message_room_topic'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='room',
            name='created',
        ),
        migrations.RemoveField(
            model_name='room',
            name='updated',
        ),
        migrations.AddField(
            model_name='room',
            name='participants',
            field=models.ManyToManyField(blank=True, related_name='participants', to=settings.AUTH_USER_MODEL),
        ),
    ]
