from django.contrib import admin
from django.urls import path, include
from api.views import survey_views

urlpatterns = [
    path("", survey_views.survey_list_create, name='survey-list-create'),
    path("<int:pk>", survey_views.survey_detail, name='survey-detail'),
]