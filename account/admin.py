from django.contrib import admin
from .models import *

# Register your models here.
class ProfAdmin(admin.ModelAdmin):
    list_display = ('id','user','banc','role','compte')

admin.site.register(Prof,ProfAdmin)