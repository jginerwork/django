import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from snippets.models import Following, Snippet


@pytest.fixture
def user_follower(db):
    return User.objects.create_user(username="follower", password="pw")


@pytest.fixture
def user_target(db):
    return User.objects.create_user(username="target", password="pw")


@pytest.mark.django_db
def test_follow_unfollow_toggle(client, user_follower, user_target):
    client.force_login(user_follower)
    url = reverse("snippets:user-follow", args=[user_target.id])

    # 1. Follow
    response = client.post(url)
    assert response.status_code == 201
    assert Following.objects.filter(
        user_follower=user_follower, user_followed=user_target
    ).exists()

    # 2. Unfollow (Toggle)
    response = client.post(url)
    assert response.status_code == 204  # Tu vista devuelve 204 al borrar
    assert not Following.objects.filter(
        user_follower=user_follower, user_followed=user_target
    ).exists()


@pytest.mark.django_db
def test_filter_following_feed(client, user_follower, user_target):
    """
    Verifica el endpoint 'filter_following' que muestra snippets de gente a la que sigues.
    """
    # Snippet del usuario objetivo
    Snippet.objects.create(
        owner=user_target, title="Target Snippet", code="x", draft=False
    )
    # Snippet de un desconocido
    unknown = User.objects.create_user(username="unknown")
    Snippet.objects.create(
        owner=unknown, title="Unknown Snippet", code="y", draft=False
    )

    client.force_login(user_follower)

    # Aún no seguimos a nadie
    url = reverse("snippets:snippet-filter-following")
    response = client.get(url)
    assert len(response.json()) == 0

    # Seguimos al target
    Following.objects.create(user_follower=user_follower, user_followed=user_target)

    # Ahora debe aparecer
    response = client.get(url)
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Target Snippet"
