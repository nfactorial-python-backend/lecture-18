from django.urls import path

from . import views

app_name = "polls"
urlpatterns = [
    path("", views.index, name="index"),
    path("<int:question_id>/details", views.detail, name="detail"),
    path("<int:question_id>/vote", views.vote, name="vote"),
    path("<int:question_id>/results", views.results, name="results"),
    path("questions/", views.add_question, name="question"),
    path(
        "questions/<int:question_id>",
        views.QuestionEditView.as_view(),
        name="question_edit",
    ),
    path("sign-up/", views.sign_up, name="sign_up"),
    path("<int:question_id>/delete", views.delete_question, name="delete"),


    path("api/", views.api_index, name="api_index"),
    path("api/post", views.api_post, name="api_post"),
    # path("api/questions/<int:pk>/", views.api_question_detail, name="api_question_detail"),
    path("api/questions/<int:pk>/", views.QuestionDetailView.as_view(), name="api_question_detail"),
    path("api/questions/", views.QuestionList.as_view(), name="api_question_list"),
]
