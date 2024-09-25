# Generated by Django 5.1.1 on 2024-09-25 18:05

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DicomStudyModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=1024)),
                ('study_instance_uid', models.CharField(max_length=1024, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='FileModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(editable=False, max_length=256)),
                ('path', models.CharField(editable=False, max_length=2048, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='LogOutputModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('timestamp', models.DateTimeField()),
                ('message', models.CharField(editable=False, max_length=1024)),
            ],
        ),
        migrations.CreateModel(
            name='DicomSeriesModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=1024)),
                ('modality', models.CharField(max_length=256)),
                ('image_type', models.CharField(max_length=1024)),
                ('series_instance_uid', models.CharField(max_length=1024, unique=True)),
                ('study', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.dicomstudymodel')),
            ],
        ),
        migrations.CreateModel(
            name='DicomImageModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('instance_uid', models.CharField(max_length=1024, unique=True)),
                ('series', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.dicomseriesmodel')),
                ('file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.filemodel')),
            ],
        ),
        migrations.CreateModel(
            name='FileSetModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=1024)),
                ('path', models.CharField(editable=False, max_length=2048, null=True, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('public', models.BooleanField(default=False)),
                ('owner', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='filemodel',
            name='fileset',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.filesetmodel'),
        ),
        migrations.CreateModel(
            name='PatientCohortModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=1024)),
                ('fileset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.filesetmodel')),
            ],
        ),
        migrations.CreateModel(
            name='PatientModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=1024)),
                ('patient_id', models.CharField(max_length=1024)),
                ('cohort', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.patientcohortmodel')),
            ],
        ),
        migrations.AddField(
            model_name='dicomstudymodel',
            name='patient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.patientmodel'),
        ),
    ]
