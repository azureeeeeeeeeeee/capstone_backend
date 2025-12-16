from django.urls import path
from api.views import ml_views

urlpatterns = [
    path('classification/predict/', ml_views.classification_predict, name='classification-predict'),
    path('classification/info/', ml_views.classification_info, name='classification-info'),
    
    path('clustering/predict/', ml_views.clustering_predict, name='clustering-predict'),
    path('clustering/info/', ml_views.clustering_info, name='clustering-info'),
    
    path('forecast/', ml_views.forecast_get, name='forecast-get'),
    path('forecast/custom/', ml_views.forecast_custom, name='forecast-custom'),
    path('forecast/info/', ml_views.forecast_info, name='forecast-info'),
    
    path('health/', ml_views.ml_health_check, name='ml-health-check'),
]
