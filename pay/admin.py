from django.contrib import admin
from .models import Department, Student

# Register your models here.

admin.site.register(Student)
admin.site.register(Department)