from django.urls import path

from . import views

app_name = "polls"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    # CAMBIO AQUÍ: de <int:question_id> a <int:pk>
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    # CAMBIO AQUÍ: de <int:question_id> a <int:pk>
    path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
    # ESTE SE DEJA IGUAL: porque la función 'vote' en views.py recibe 'question_id'
    path("<int:question_id>/vote/", views.vote, name="vote"),
]
