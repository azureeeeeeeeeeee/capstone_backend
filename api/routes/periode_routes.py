from django.urls import path
from api.views import periode_views

urlpatterns = [
    path('', periode_views.periode_list, name='periode-list'),
    path('<int:pk>/', periode_views.periode_detail, name='periode-detail'),
]