from django.urls import path
from api.views import unit_views

urlpatterns = [
    # Faculty endpoints
    path('faculties/', unit_views.faculty_list, name='faculty-list'),
    path('faculties/<int:pk>/', unit_views.faculty_detail, name='faculty-detail'),

    # Program Study endpoints
    path('program-studies/', unit_views.program_study_list, name='programstudy-list'),
    path('program-studies/<int:pk>/', unit_views.program_study_detail, name='programstudy-detail'),
]