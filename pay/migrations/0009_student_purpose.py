# Generated by Django 4.0.1 on 2022-02-08 08:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pay', '0008_department_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='purpose',
            field=models.CharField(default='BASIC DUES AND CONFERENCE', max_length=150, null=True),
        ),
    ]
