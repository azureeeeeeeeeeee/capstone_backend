from django.contrib import admin
from api.models import ProgramStudy, Faculty, Survey, ProgramSpecificQuestion, Periode, Section, Question, Answer, Department

# Register your models here.
admin.site.register(ProgramStudy)
admin.site.register(Department)
admin.site.register(Faculty)
admin.site.register(Survey)
admin.site.register(Section)
admin.site.register(Question)
admin.site.register(ProgramSpecificQuestion)
admin.site.register(Periode)
admin.site.register(Answer)