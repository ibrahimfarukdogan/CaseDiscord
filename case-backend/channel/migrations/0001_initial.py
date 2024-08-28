# Generated by Django 5.0.7 on 2024-08-15 08:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('group', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DiscordChannel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Channel Name')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('token', models.CharField(max_length=500, verbose_name='Token')),
                ('token_type', models.CharField(choices=[('bearer', 'Bearer'), ('oauth2', 'Oauth2'), ('id', 'ID')], max_length=255, verbose_name='Token Type')),
                ('token_secret', models.CharField(blank=True, max_length=500, null=True, verbose_name='Token Secret')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created Date')),
                ('status', models.BooleanField(default=True)),
                ('added_by_group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='group.workgroup', verbose_name='Organization')),
                ('added_by_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
        ),
    ]
