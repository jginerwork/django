import json
import pytest
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from snippets.models import Notification, Snippet


@pytest.fixture
def user_a(db):
    return User.objects.create_user(username="user_a", password="password123")


@pytest.fixture
def user_b(db):
    return User.objects.create_user(username="user_b", password="password123")


@pytest.fixture
def snippet_b(db, user_b):
    return Snippet.objects.create(
        owner=user_b, title="Snippet B", code="print('B')", draft=False
    )


@pytest.mark.django_db
def test_signal_comment_creates_notification(client, user_a, user_b, snippet_b):
    """
    Verifica que cuando user_a comenta en el snippet de user_b,
    se crea una notificación para user_b.
    """
    client.force_login(user_a)
    url = reverse("snippets:snippet-add-comment", args=[snippet_b.id])
    data = {"text": "Great code!"}

    # 1. Crear comentario
    response = client.post(url, data=json.dumps(data), content_type="application/json")
    assert response.status_code == 201

    # 2. Verificar Signal
    # Debe haber 1 notificación dirigida a user_b
    assert Notification.objects.count() == 1
    notif = Notification.objects.first()
    assert notif.recipient == user_b
    assert notif.actor == user_a
    assert notif.verb == "has commented on your snippet"
    assert notif.target == snippet_b


@pytest.mark.django_db
def test_signal_self_comment_no_notification(client, user_b, snippet_b):
    """
    Verifica que si uno comenta en su propio snippet, NO se crea notificación.
    """
    client.force_login(user_b)
    url = reverse("snippets:snippet-add-comment", args=[snippet_b.id])
    data = {"text": "My own comment"}

    client.post(url, data=json.dumps(data), content_type="application/json")

    assert Notification.objects.count() == 0


@pytest.mark.django_db
def test_signal_follow_creates_notification(client, user_a, user_b):
    """
    Verifica que cuando user_a sigue a user_b, se crea notificación para user_b.
    """
    client.force_login(user_a)
    url = reverse(
        "snippets:user-follow", args=[user_b.id]
    )  # Action 'follow' en UserViewSet

    # 1. Seguir
    response = client.post(url)
    assert response.status_code == 201

    # 2. Verificar Signal
    assert Notification.objects.count() == 1
    notif = Notification.objects.first()
    assert notif.recipient == user_b
    assert notif.actor == user_a
    assert notif.verb == "has started following you"
    assert notif.target == user_a  # En signals.py target es user_follower


@pytest.mark.django_db
def test_notification_viewset_filter(client, user_a, user_b):
    """
    Verifica que cada usuario solo ve SUS notificaciones.
    """
    snippet_ct = ContentType.objects.get_for_model(Snippet)
    # Creamos notificación manual para user_a
    Notification.objects.create(
        recipient=user_a,
        actor=user_b,
        verb="test",
        content_type=snippet_ct,
        object_id=1,
    )
    # Creamos notificación manual para user_b
    Notification.objects.create(
        recipient=user_b,
        actor=user_a,
        verb="test",
        content_type=snippet_ct,
        object_id=1,
    )

    # 1. Login user_a
    client.force_login(user_a)
    url = reverse("snippets:notification-list")
    response = client.get(url)

    # user_a solo debe ver 1
    assert response.status_code == 200
    assert len(response.json()["results"]) == 1
    assert response.json()["results"][0]["actor"] == "user_b"
