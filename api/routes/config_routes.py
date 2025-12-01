from django.urls import path
from api.views.config_views import system_config_list, system_config_detail

urlpatterns = [
    path("", system_config_list, name="system-config-list"),
    path("<int:pk>/", system_config_detail, name="system-config-detail"),
]