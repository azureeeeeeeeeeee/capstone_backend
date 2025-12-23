from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("surveys/", include("api.routes.survey_routes")),
    path("unit/", include("api.routes.unit_routes")),
    path("periodes/", include("api.routes.periode_routes")),
    path("", include("api.routes.user_role_routes")),
    path("configs/", include("api.routes.config_routes")),
    path("ml/", include("api.routes.ml_routes")),
    path("mailer/", include("api.routes.mail_routes")),
]