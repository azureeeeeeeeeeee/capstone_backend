from django.contrib import admin
from django.urls import path, include
from api.views import survey_views

urlpatterns = [
    # Surveys
    path("", survey_views.survey_list_create, name='survey-list-create'),
    path("<int:pk>", survey_views.survey_detail, name='survey-detail'),

    # Sections
    path("sections/", survey_views.section_list_create, name='section-list-create'),
    path("sections/<int:pk>", survey_views.section_detail, name='section-detail'),
]
