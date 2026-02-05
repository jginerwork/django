import json
import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from snippets.models import book, editorial


@pytest.fixture
def library_user(db):
    return User.objects.create_user(username="lib_user", password="pw")


@pytest.fixture
def editor(db):
    return editorial.objects.create(name="Penguin", email="p@test.com")


@pytest.fixture
def book_inst(db, library_user, editor):
    # Nota: el modelo 'book' requiere un author (User) por defecto Anonymous si no se pasa,
    # pero aquí lo pasamos explícito.
    return book.objects.create(
        title="Django 101", author=library_user, editorial=editor
    )


@pytest.mark.django_db
def test_create_editorial(client):
    url = reverse("snippets:editorial-list")
    data = {
        "name": "OReilly",
        "email": "o@test.com",
        "countries": [],
    }  # M2M countries vacio

    response = client.post(url, json.dumps(data), content_type="application/json")
    assert response.status_code == 201
    assert editorial.objects.count() == 1


@pytest.mark.django_db
def test_create_book_with_relations(client, library_user, editor):
    """
    Test de creación con HyperlinkedModelSerializer.
    Necesitamos pasar las URLs de las relaciones, no los IDs.
    """
    url_book_list = reverse("snippets:book-list")

    # Construimos las URLs esperadas por el serializer
    # user-detail y editorial-detail
    author_url = reverse("snippets:user-detail", args=[library_user.id])
    # Como es un test, el dominio suele ser http://testserver
    # A veces DRF acepta path relativo, pero lo correcto es full URL o path absoluto.
    # El cliente de test maneja paths relativos bien.

    editorial_url = reverse("snippets:editorial-detail", args=[editor.id])

    data = {
        "title": "Test Driven Python",
        "author": f"http://testserver{author_url}",
        "editorial": f"http://testserver{editorial_url}",
    }

    response = client.post(
        url_book_list, json.dumps(data), content_type="application/json"
    )

    assert response.status_code == 201
    assert book.objects.count() == 1
    new_book = book.objects.first()
    assert new_book.title == "Test Driven Python"
    assert new_book.editorial == editor


@pytest.mark.django_db
def test_opinion_crud(client, library_user, book_inst):
    client.force_login(library_user)
    url = reverse("snippets:opinion-list")
    book_url = reverse("snippets:book-detail", args=[book_inst.id])

    data = {
        "title": "Great book",
        "text": "Loved it",
        "rating": 5,  # Rating es IntegerField con choices
        "book": f"http://testserver{book_url}",
    }

    # 1. Crear
    response = client.post(url, json.dumps(data), content_type="application/json")
    assert response.status_code == 201

    # 2. Listar
    response = client.get(url)
    assert len(response.json()["results"]) == 1
