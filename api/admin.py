from django.contrib import admin
from api.models import ProgramStudy, Faculty, Survey, ProgramSpecificQuestion, Periode

# Register your models here.
admin.site.register(ProgramStudy)
admin.site.register(Faculty)
admin.site.register(Survey)
admin.site.register(ProgramSpecificQuestion)
admin.site.register(Periode)