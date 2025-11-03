from django.urls import path
from api.views import survey_views as views

urlpatterns = [
    # ---- Survey ----
    path("", views.survey_list_create, name="survey-list-create"),
    path("<int:pk>/", views.survey_detail, name="survey-detail"),

    # ---- Section ----
    path("<int:survey_id>/sections/", views.section_list_create, name="section-list-create"),
    path("<int:survey_id>/sections/<int:pk>/", views.section_detail, name="section-detail"),

    # ---- Question ----
    path("<int:survey_id>/sections/<int:section_id>/questions/", views.question_list_create, name="question-list-create"),
    path("<int:survey_id>/sections/<int:section_id>/questions/<int:pk>/", views.question_detail, name="question-detail"),
]
