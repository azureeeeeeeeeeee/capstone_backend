from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("surveys/", include("api.routes.survey_routes")),
]