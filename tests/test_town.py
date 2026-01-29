import pytest
from django.urls import reverse 
from snippets.models import region, country, town, town, municipality
import snippets.urls
import json

@pytest.mark.django_db
def test_get_town_OK_GET(client):
    c = country.objects.create(name='Spain')
    r = region.objects.create(name = 'Barcelona', country = c)
    t = town.objects.create(name = 'Terrassa', region = r, population= 200)

    url = reverse('snippets:get-town')

    response = client.get(url)

    assert response.status_code == 200

@pytest.mark.django_db
def test_get_town_GET_OK_EMPTY(client):
    url = reverse('snippets:get-town')

    response = client.get(url)

    assert response.status_code == 200

@pytest.mark.django_db
def test_get_town_GET_CONTENT(client):
    c = country.objects.create(name='Spain')
    r = region.objects.create(name = 'Barcelona', country = c)
    t = town.objects.create(name = 'Terrassa', region = r, population= 200)

    url = reverse('snippets:get-town')

    response = client.get(url)

    resp_json = response.json()

    assert resp_json['results'][0]['name'] == t.name
    assert resp_json['results'][0]['region'] == t.region.id
    assert resp_json['results'][0]['population'] == t.population

@pytest.mark.django_db
def test_get_town_POST_OK(client):
    c = country.objects.create(name='Spain')
    r = region.objects.create(name = 'Barcelona', country = c)

    body = {'name': 'Terrassa', 'region': r.id, 'population': 200}

    url = reverse('snippets:get-town')

    response = client.post(url, json.dumps(body), content_type = 'application/json')

    assert response.status_code == 201

@pytest.mark.django_db
def test_get_town_POST_ERROR_UNIQUE(client):
    c = country.objects.create(name = 'Spain')
    r = region.objects.create(name = 'Barcelona', country = c)
    t = town.objects.create(name = 'Terrassa', region = r, population = 2000)

    body = {'name': 'Terrassa', 'region': r.id, 'population': 2000}

    url = reverse('snippets:get-town')

    response = client.post(url, json.dumps(body), content_type = 'application/json')

    assert response.status_code == 400

@pytest.mark.django_db
def test_get_town_POST_ERROR_POPULATION(client):
    c = country.objects.create(name = 'Spain')
    r = region.objects.create(name = 'Barcelona', country = c)

    body = {'name': 'Terrassa', 'region': r.id, 'population': 230000}

    url = reverse('snippets:get-town')

    response = client.post(url, json.dumps(body), content_type = 'application/json')

    assert response.status_code == 400

@pytest.mark.django_db
def test_get_town_LIMIT_OK(client):
    c = country.objects.create(name = 'Spain')
    r = region.objects.create(name = 'Barcelona', country = c)

    body = {'name': 'Town1', 'region': r.id, 'population': 9999}

    url = reverse('snippets:get-town')

    response = client.post(url, json.dumps(body), content_type = 'application/json')

    assert response.status_code == 201

@pytest.mark.django_db
def test_get_town_LIMIT_ERROR(client):
    c = country.objects.create(name = 'Spain')
    r = region.objects.create(name = 'Barcelona', country = c)

    body = {'name': 'Town1', 'region': r.id, 'population': 10000}

    url = reverse('snippets:get-town')

    response = client.post(url, json.dumps(body), content_type = 'application/json')

    assert response.status_code == 400

@pytest.mark.django_db
def test_get_town_NEGATIVE_ERROR(client):
    c = country.objects.create(name = 'Spain')
    r = region.objects.create(name = 'Barcelona', country = c)

    body = {'name': 'Town1', 'region': r.id, 'population': -1}

    url = reverse('snippets:get-town')

    response = client.post(url, json.dumps(body), content_type = 'application/json')

    assert response.status_code == 400

@pytest.mark.django_db
def test_get_town_DELETE_CASCADE(client):
    c = country.objects.create(name = 'Spain')
    r = region.objects.create(name = 'Barcelona', country = c)
    t = town.objects.create(name = 'Town1', population = 10, region = r)

    assert town.objects.count() == 1

    c.delete()

    assert town.objects.count() == 0

@pytest.mark.django_db
def test_get_town_POST_CAPITALIZE(client):
    c = country.objects.create(name = 'Spain')
    r = region.objects.create(name = 'Barcelona', country = c)

    url = reverse('snippets:get-town')

    body = {'name': 'town1', 'region': r.id, 'population': 9999}

    response = client.post(url, json.dumps(body), content_type = 'application/json')

    assert response.json()['name'] == body['name'].title()
    assert response.status_code == 201