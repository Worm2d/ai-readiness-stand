from django.urls import path

from . import views

urlpatterns = [
    path("survey/start/", views.SurveyStartView.as_view(), name="survey_start"),
    path("survey/<uuid:session_uuid>/question/<int:step>/", views.SurveyQuestionView.as_view(), name="survey_question"),
    path("survey/<uuid:session_uuid>/contacts/", views.SurveyContactsView.as_view(), name="survey_contacts"),
    path(
        "survey/<uuid:session_uuid>/contacts/anonymous/",
        views.SurveyAnonymousContinueView.as_view(),
        name="survey_contacts_anonymous",
    ),
    path("survey/<uuid:session_uuid>/result/", views.SurveyResultView.as_view(), name="survey_result"),
]
