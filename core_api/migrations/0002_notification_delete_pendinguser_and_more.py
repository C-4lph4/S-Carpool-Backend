# Generated by Django 5.0.4 on 2024-06-06 23:26

import datetime
import django.db.models.deletion
import django.utils.timezone
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core_api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('body', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.DeleteModel(
            name='PendingUser',
        ),
        migrations.RemoveField(
            model_name='requests',
            name='profile',
        ),
        migrations.AddField(
            model_name='activeuser',
            name='code_expires',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='activeuser',
            name='confirmation_code',
            field=models.CharField(default='', max_length=6),
        ),
        migrations.AddField(
            model_name='activeuser',
            name='is_online',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='activeuser',
            name='language',
            field=models.CharField(default='fr', max_length=2),
        ),
        migrations.AddField(
            model_name='requests',
            name='acceptor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='requests_accepted', to='core_api.profile'),
        ),
        migrations.AddField(
            model_name='requests',
            name='owner',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='requests_made', to='core_api.profile'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='default_req_timeout',
            field=models.DurationField(default=datetime.timedelta(seconds=1800)),
        ),
        migrations.AlterField(
            model_name='requests',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='requests',
            name='message',
            field=models.TextField(max_length=1000),
        ),
        migrations.AddField(
            model_name='notification',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
