# Generated by Django 4.2.4 on 2023-09-02 20:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pay', '0012_alter_student_purpose'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='_paid_basic',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='_paid_conference',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='_paid_dinner',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='total_amount',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
