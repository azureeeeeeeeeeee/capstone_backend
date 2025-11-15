from django.urls import path
from api.views import unit_views

urlpatterns = [
    path('faculties/', unit_views.faculty_list, name='faculty-list'),
    path('faculties/<int:pk>/', unit_views.faculty_detail, name='faculty-detail'),

    path('program-studies/', unit_views.program_study_list, name='programstudy-list'),
    path('program-studies/<int:pk>/', unit_views.program_study_detail, name='programstudy-detail'),

    path('departments/', unit_views.department_list),
    path('departments/<int:pk>/', unit_views.department_detail),
]