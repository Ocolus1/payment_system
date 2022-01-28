import email
from django.db import models

# Create your models here.
class Student(models.Model):
    matric_no = models.IntegerField(null=True, unique=True)
    name = models.CharField(max_length=150, null=True)
    email = models.EmailField(max_length=100, null=True)
    level = models.IntegerField(null=True)
    amount = models.IntegerField(null=True)

    def __str__(self):
        return self.name