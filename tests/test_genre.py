import pytest
from django.urls import reverse
from snippets.models import Genre
import snippets.urls
import json

@pytest.mark.django_db
def test_create_genre_capitalize(client):
    url = reverse('snippets:genre-list')
    body = {'name': 'terror', 'description': 'libros de miedo'}

    response = client.post(url, json.dumps(body), content_type = 'application/json')

    assert response.status_code == 201
    assert response.json()['name'] == body['name'].title()
    assert response.json()['description'] == body['description'].capitalize()

    inst = Genre.objects.filter(name = body['name'].title())

    assert inst.count() == 1
    assert inst[0].name == body['name'].title()
    assert inst[0].description == body['description'].capitalize()

@pytest.mark.django_db
def test_get_genre_by_name(client):
    g = Genre.objects.create(name = 'terror', description = 'libros de miedo')

    url = reverse('snippets:genre-detail', args = [g.name])

    response = client.get(url)

    assert response.status_code == 200
    assert response.json()['name'] == g.name
    assert response.json()['description'] == g.description

@pytest.mark.django_db
def test_get_list_genres(client):
    g1 = Genre.objects.create(name = 'romance', description = 'libros de romance')
    g2 = Genre.objects.create(name = 'fantasy', description = 'libros de fantasía')

    url = reverse('snippets:genre-list')
    response = client.get(url)

    assert response.status_code == 200
    data = response.json()
    assert len(data['results']) == 2
    assert data['results'][0]['name'] == g1.name
    assert data['results'][0]['description'] == g1.description
    assert data['results'][1]['name'] == g2.name
    assert data['results'][1]['description'] == g2.description