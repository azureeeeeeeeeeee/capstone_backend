from django.urls import path
from api.views.mail_views import remind_unfinished_survey_users, remind_unfinished_by_program_study, remind_unfinished_by_users

urlpatterns = [
    path("reminder/all/", remind_unfinished_survey_users, name="mail-reminder-all"),
    path("reminder/user/<str:user_id>/", remind_unfinished_by_users, name="mail-reminder-user"),
    path("reminder/prodi/", remind_unfinished_by_program_study, name="mail-reminder-prodi"),
]