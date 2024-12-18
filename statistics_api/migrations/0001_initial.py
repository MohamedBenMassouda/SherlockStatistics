# Generated by Django 5.1.4 on 2024-12-05 23:15

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Feature',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('category', models.CharField(max_length=100)),
                ('creation_date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'indexes': [models.Index(fields=['name'], name='statistics__name_1a4f67_idx')],
            },
        ),
        migrations.CreateModel(
            name='UserFeedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=100)),
                ('rating', models.DecimalField(decimal_places=1, max_digits=2)),
                ('feedback_text', models.TextField(blank=True, null=True)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'indexes': [models.Index(fields=['category', 'rating'], name='statistics__categor_d1e308_idx')],
            },
        ),
        migrations.CreateModel(
            name='UserInteraction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interaction_type', models.CharField(choices=[('click', 'Click'), ('hover', 'Hover'), ('focus', 'Focus'), ('scroll', 'Scroll')], max_length=50)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('duration', models.IntegerField(help_text='Interaction duration in seconds')),
                ('additional_metadata', models.JSONField(blank=True, null=True)),
                ('feature', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='statistics_api.feature')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'indexes': [models.Index(fields=['user', 'feature', 'timestamp'], name='statistics__user_id_6ee92a_idx')],
            },
        ),
    ]
