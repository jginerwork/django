import json

import pytest
from django.urls import reverse

from snippets.models import city, country, region


@pytest.mark.django_db
def test_get_city_OK_GET(client):
    c = country.objects.create(name="Spain")
    r = region.objects.create(name="Barcelona", country=c)
    city.objects.create(name="Terrassa", region=r, population=200000)

    url = reverse("snippets:get-city")

    response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_get_city_GET_OK_EMPTY(client):
    url = reverse("snippets:get-city")

    response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_get_city_GET_CONTENT(client):
    c = country.objects.create(name="Spain")
    r = region.objects.create(name="Barcelona", country=c)
    ci = city.objects.create(name="Terrassa", region=r, population=200000)

    url = reverse("snippets:get-city")

    response = client.get(url)

    resp_json = response.json()

    assert resp_json["results"][0]["name"] == ci.name
    assert resp_json["results"][0]["region"] == ci.region.id
    assert resp_json["results"][0]["population"] == ci.population


@pytest.mark.django_db
def test_get_city_POST_OK(client):
    c = country.objects.create(name="Spain")
    r = region.objects.create(name="Barcelona", country=c)

    body = {"name": "Terrassa", "region": r.id, "population": 200000}

    url = reverse("snippets:get-city")

    response = client.post(url, json.dumps(body), content_type="application/json")

    assert response.status_code == 201


@pytest.mark.django_db
def test_get_city_POST_ERROR_UNIQUE(client):
    c = country.objects.create(name="Spain")
    r = region.objects.create(name="Barcelona", country=c)
    city.objects.create(name="Terrassa", region=r, population=200000)

    body = {"name": "Terrassa", "region": r.id, "population": 200000}

    url = reverse("snippets:get-city")

    response = client.post(url, json.dumps(body), content_type="application/json")

    assert response.status_code == 400


@pytest.mark.django_db
def test_get_city_POST_ERROR_POPULATION(client):
    c = country.objects.create(name="Spain")
    r = region.objects.create(name="Barcelona", country=c)

    body = {"name": "Terrassa", "region": r.id, "population": 23}

    url = reverse("snippets:get-city")

    response = client.post(url, json.dumps(body), content_type="application/json")

    assert response.status_code == 400


@pytest.mark.django_db
def test_get_city_LIMIT_OK(client):
    c = country.objects.create(name="Spain")
    r = region.objects.create(name="Barcelona", country=c)

    body = {"name": "city1", "region": r.id, "population": 10000}

    url = reverse("snippets:get-city")

    response = client.post(url, json.dumps(body), content_type="application/json")

    assert response.status_code == 201


@pytest.mark.django_db
def test_get_city_LIMIT_ERROR(client):
    c = country.objects.create(name="Spain")
    r = region.objects.create(name="Barcelona", country=c)

    body = {"name": "city1", "region": r.id, "population": 9999}

    url = reverse("snippets:get-city")

    response = client.post(url, json.dumps(body), content_type="application/json")

    assert response.status_code == 400


@pytest.mark.django_db
def test_get_city_NEGATIVE_ERROR(client):
    c = country.objects.create(name="Spain")
    r = region.objects.create(name="Barcelona", country=c)

    body = {"name": "city1", "region": r.id, "population": -20000}

    url = reverse("snippets:get-city")

    response = client.post(url, json.dumps(body), content_type="application/json")

    assert response.status_code == 400


@pytest.mark.django_db
def test_get_city_DELETE_CASCADE(client):
    c = country.objects.create(name="Spain")
    r = region.objects.create(name="Barcelona", country=c)
    city.objects.create(name="city1", region=r, population=200000)

    assert city.objects.count() == 1

    c.delete()

    assert city.objects.count() == 0


@pytest.mark.django_db
def test_get_city_POST_CAPITALIZE(client):
    c = country.objects.create(name="Spain")
    r = region.objects.create(name="Barcelona", country=c)

    body = {"name": "city1", "region": r.id, "population": 200000}

    url = reverse("snippets:get-city")

    response = client.post(url, json.dumps(body), content_type="application/json")

    assert response.status_code == 201
    assert response.json()["name"] == body["name"].title()
