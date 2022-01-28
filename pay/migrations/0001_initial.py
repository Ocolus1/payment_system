# Generated by Django 4.0.1 on 2022-01-23 21:20

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('matric_no', models.IntegerField(max_length=50, null=True, unique=True)),
                ('first_name', models.CharField(max_length=50, null=True)),
                ('last_name', models.CharField(max_length=50, null=True)),
                ('email', models.EmailField(max_length=100, null=True)),
                ('level', models.IntegerField(null=True)),
                ('amount', models.IntegerField(max_length=50, null=True)),
            ],
        ),
    ]
