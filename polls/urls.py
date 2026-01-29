from django.urls import path, include
from polls import views
from django.contrib import admin

app_name = "polls"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"), #al anar a aquesta url, django executa la funció index
    path("<int:question_id>/", views.DetailView.as_view(), name="detail"),
    path("<int:question_id>/results/", views.ResultsView.as_view(), name = "results"),
    path("<int:question_id>/vote/", views.vote, name="vote"),
]