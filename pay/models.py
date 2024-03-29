import email
from wsgiref.simple_server import demo_app
from django.db import models

# Create your models here.
class Student(models.Model):
    matric_no = models.IntegerField(null=True, unique=True)
    name = models.CharField(max_length=150, null=True)
    email = models.EmailField(max_length=100, null=True)
    phone = models.CharField(null=True, max_length=15, default="08090989808")
    level = models.IntegerField(null=True)
    amount = models.IntegerField(null=True, blank=True)
    total_amount = models.IntegerField(null=True, blank=True)
    purpose = models.CharField(max_length=150, null=True, blank=True)
    paid_basic = models.BooleanField(default=False)
    paid_conference = models.BooleanField(default=False)
    paid_dinner = models.BooleanField(default=False)
    
    _paid_basic = models.BooleanField(default=False, null=True, blank=True)
    _paid_conference = models.BooleanField(default=False, null=True, blank=True)
    _paid_dinner = models.BooleanField(default=False, null=True, blank=True)
    ref = models.CharField(max_length=500, null=True, default="REFERENCE NUM")
    dept = models.CharField(max_length=500, null=True, default="TESA")
    paid_date = models.CharField(max_length=500, null=True, blank=True)
    pub_date = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.name} - {self.email} - {self.level}"

class Department(models.Model):
    name = models.CharField(max_length=150, null=True)
    short_name = models.CharField(max_length=150, null=True)
    email = models.EmailField(max_length=100, null=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    avatar = models.ImageField(upload_to='images/%Y/%m/%d', default="images/avatar.jpg", blank=True)
    sign = models.ImageField(upload_to='images/%Y/%m/%d', default="images/avatar.jpg", blank=True)
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name