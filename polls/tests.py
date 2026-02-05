import pytest
from . import views
from .models import Choice, Question
from django.test import RequestFactory
from django.urls import reverse
from django.utils import timezone


# Marcamos que estos tests necesitan acceso a la base de datos
@pytest.mark.django_db
class TestPolls:

    # --- TESTS PARA LAS VISTAS BASADAS EN CLASES (USADAS EN URLS.PY) ---

    def test_index_view_with_no_questions(self, client):
        """Prueba que IndexView funciona sin preguntas."""
        # Esto cubre polls/urls.py línea 8 y views.py IndexView
        url = reverse("polls:index")
        response = client.get(url)
        assert response.status_code == 200
        assert "latest_question_list" in response.context
        assert len(response.context["latest_question_list"]) == 0

    def test_index_view_with_questions(self, client):
        """Prueba que IndexView muestra preguntas pasadas y filtra futuras."""
        # Creamos una pregunta en el pasado
        q = Question.objects.create(
            question_text="Past?", pub_date=timezone.now() - timezone.timedelta(days=1)
        )
        # Creamos una pregunta en el futuro (no debería salir según views.py línea 54)
        Question.objects.create(
            question_text="Future?",
            pub_date=timezone.now() + timezone.timedelta(days=1),
        )

        response = client.get(reverse("polls:index"))
        assert list(response.context["latest_question_list"]) == [q]

    def test_detail_view_success(self, client):
        """Prueba DetailView con una pregunta válida."""
        # Cubre polls/urls.py línea 9 y views.py DetailView
        q = Question.objects.create(question_text="Q1", pub_date=timezone.now())
        url = reverse("polls:detail", args=(q.id,))
        response = client.get(url)
        assert response.status_code == 200
        assert response.context["question"] == q

    def test_detail_view_404_future_question(self, client):
        """Prueba que DetailView da 404 si la pregunta es futura (según views.py linea 61)."""
        future_q = Question.objects.create(
            question_text="Future", pub_date=timezone.now() + timezone.timedelta(days=1)
        )
        url = reverse("polls:detail", args=(future_q.id,))
        response = client.get(url)
        assert response.status_code == 404

    def test_results_view(self, client):
        """Prueba ResultsView."""
        # Cubre polls/urls.py línea 10 y views.py ResultsView
        q = Question.objects.create(question_text="Q1", pub_date=timezone.now())
        url = reverse("polls:results", args=(q.id,))
        response = client.get(url)
        assert response.status_code == 200

    # --- TESTS PARA LA FUNCIÓN VOTE (Lógica compleja) ---

    def test_vote_success(self, client):
        """Prueba el flujo correcto de votación."""
        # Cubre polls/urls.py línea 11 y views.py def vote (éxito)
        q = Question.objects.create(question_text="Vote Q", pub_date=timezone.now())
        c = Choice.objects.create(question=q, choice_text="C1", votes=0)

        url = reverse("polls:vote", args=(q.id,))
        # Enviamos POST con la opción seleccionada
        response = client.post(url, {"choice": c.id})

        # Debe redirigir (código 302) a results
        assert response.status_code == 302
        assert response.url == reverse("polls:results", args=(q.id,))

        # Verificar que el voto se sumó (views.py líneas 39-40)
        c.refresh_from_db()
        assert c.votes == 1

    def test_vote_failure_no_choice(self, client):
        """Prueba el error cuando no se selecciona opción."""
        # Cubre views.py líneas 35-37 (KeyError/DoesNotExist)
        q = Question.objects.create(question_text="Vote Q", pub_date=timezone.now())
        url = reverse("polls:vote", args=(q.id,))

        # POST sin datos
        response = client.post(url, {})

        assert response.status_code == 400
        assert response.content == b"You didn't select a choice."

    def test_vote_failure_invalid_choice(self, client):
        """Prueba el error cuando la opción no existe (Choice.DoesNotExist)."""
        q = Question.objects.create(question_text="Vote Q", pub_date=timezone.now())
        url = reverse("polls:vote", args=(q.id,))

        # POST con ID que no existe
        response = client.post(url, {"choice": 9999})

        assert response.status_code == 400

    # --- TESTS PARA CÓDIGO "NO USADO" (Para lograr 100% Coverage) ---
    # Estas funciones (detail, results, index) existen en views.py pero
    # urls.py no apunta a ellas. Hay que llamarlas manualmente.

    def test_legacy_functions(self):
        """Test directo a las funciones antiguas en views.py."""
        factory = RequestFactory()
        request = factory.get("/")

        # 1. Testear def detail(request, question_id) - views.py linea 25
        response_detail = views.detail(request, 1)
        assert response_detail.status_code == 200
        assert b"You're looking at question 1" in response_detail.content

        # 2. Testear def results(request, question_id) - views.py linea 28
        response_results = views.results(request, 1)
        assert response_results.status_code == 200
        assert (
            b"You're looking at the results of question 1" in response_results.content
        )

        # 3. Testear def index(request) - views.py linea 45
        # Necesitamos preguntas para la línea 47
        Question.objects.create(question_text="Legacy Q", pub_date=timezone.now())
        response_index = views.index(request)
        assert response_index.status_code == 200
        assert b"Legacy Q" in response_index.content
