from django.contrib import admin
from .models import Company,Student,PlacementApplication

# Register your models here.

admin.site.register(Company)
admin.site.register(Student)
admin.site.register(PlacementApplication)