import json

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from snippets.models import Comment, Snippet


@pytest.fixture
def user(db):
    return User.objects.create_user(username="commenter", password="pw")


@pytest.fixture
def snippet(db, user):
    return Snippet.objects.create(owner=user, title="S1", code="c", draft=False)


@pytest.mark.django_db
def test_create_parent_comment(client, user, snippet):
    """
    Prueba crear un comentario raíz en un snippet.
    """
    client.force_login(user)
    # Usamos la action 'add_comment' del SnippetViewSet
    url = reverse("snippets:snippet-add-comment", args=[snippet.id])
    data = {"text": "Root comment"}

    response = client.post(url, json.dumps(data), content_type="application/json")

    assert response.status_code == 201
    assert Comment.objects.count() == 1
    c = Comment.objects.first()
    assert c.text == "Root comment"
    assert c.snippet == snippet
    assert c.parent is None


@pytest.mark.django_db
def test_create_reply_comment(client, user, snippet):
    """
    Prueba crear una RESPUESTA a un comentario existente.
    """
    # 1. Crear comentario padre
    parent = Comment.objects.create(owner=user, snippet=snippet, text="Parent")

    client.force_login(user)
    # Usamos la action 'add_comment' del CommentViewSet (para replies)
    url = reverse("snippets:comment-add-comment", args=[parent.id])
    data = {"text": "Reply comment"}

    response = client.post(url, json.dumps(data), content_type="application/json")

    assert response.status_code == 201

    # Verificar estructura
    reply = Comment.objects.last()
    assert reply.text == "Reply comment"
    assert reply.parent == parent
    assert reply.snippet == snippet  # Debe heredar el snippet del padre


@pytest.mark.django_db
def test_comment_threading_serializer(client, user, snippet):
    """
    Verifica que el serializer anida las respuestas dentro del padre.
    """
    parent = Comment.objects.create(owner=user, snippet=snippet, text="Parent")
    Comment.objects.create(owner=user, snippet=snippet, text="Reply", parent=parent)

    # Obtenemos el detalle del snippet, que incluye comments (según SnippetSerializer)
    # OJO: Tu SnippetSerializer incluye 'comments' pero el test de threading
    # se ve mejor llamando al CommentViewSet o viendo el JSON del snippet.

    # Vamos a pedir el detalle del comentario padre directamente si estuviera expuesto,
    # pero como CommentViewSet es GenericViewSet con mixins, probamos retrieve.
    url = reverse("snippets:comment-detail", args=[parent.id])
    client.force_login(user)
    response = client.get(url)

    assert response.status_code == 200
    data = response.json()

    # Verificar recursividad
    assert len(data["replies"]) == 1
    assert data["replies"][0]["text"] == "Reply"


@pytest.mark.django_db
def test_comment_like_toggle(client, user, snippet):
    """
    Prueba dar y quitar like a un comentario.
    """
    comment = Comment.objects.create(owner=user, snippet=snippet, text="Like me")
    client.force_login(user)
    url = reverse("snippets:comment-like", args=[comment.id])

    # 1. Like
    response = client.post(url)
    assert response.status_code == 204
    assert comment.like.count() == 1

    # 2. Unlike
    response = client.post(url)
    assert response.status_code == 204
    assert comment.like.count() == 0
