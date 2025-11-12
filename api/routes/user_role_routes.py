from django.urls import path
from api.views import user_role_views

urlpatterns = [
    path('roles/', user_role_views.role_list_create, name='role-list-create'),
    path('roles/<int:pk>/', user_role_views.role_detail, name='role-detail'),

    path('users/', user_role_views.user_list_create, name='user-list-create'),
    path('users/<str:pk>/', user_role_views.user_detail, name='user-detail'),
]