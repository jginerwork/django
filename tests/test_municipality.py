import json
import pytest
from django.urls import reverse
from snippets.models import city, country, region, town


@pytest.mark.django_db
def test_get_municipality_OK_CITY(client):
    c = country.objects.create(name="Spain")
    r = region.objects.create(name="Barcelona", country=c)
    city.objects.create(name="Terrassa", region=r, population=200000)

    url = reverse("snippets:get-municipality")
    response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_get_municipality_OK_TOWN(client):
    c = country.objects.create(name="Spain")
    r = region.objects.create(name="Lleida", country=c)
    town.objects.create(name="Olp", region=r, population=20)

    url = reverse("snippets:get-municipality")
    response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_get_municipality_ERROR_METHOD_POST(client):
    c = country.objects.create(name="Spain")
    region.objects.create(name="Barcelona", country=c)

    body = {"name": "Terrassa", "region": "Barcelona"}

    url = reverse("snippets:get-municipality")

    response = client.post(url, data=json.dumps(body), content_type="application/json")

    assert response.status_code == 405


@pytest.mark.django_db
def test_get_municipality_ERROR_METHOD_DELETE_CITY(client):
    c = country.objects.create(name="Spain")
    r = region.objects.create(name="Barcelona", country=c)
    city.objects.create(name="Terrassa", region=r, population=200000)

    url = reverse("snippets:get-municipality")

    response = client.delete(url)

    assert response.status_code == 405


@pytest.mark.django_db
def test_get_municipality_ERROR_METHOD_DELETE_TOWN(client):
    c = country.objects.create(name="Spain")
    r = region.objects.create(name="Barcelona", country=c)
    town.objects.create(name="Vacarisses", population=2000, region=r)

    url = reverse("snippets:get-municipality")

    response = client.delete(url)

    assert response.status_code == 405


@pytest.mark.django_db
def test_get_municipality_CONTENT_CITY(client):
    c = country.objects.create(name="Spain")
    r = region.objects.create(name="Barcelona", country=c)
    ci = city.objects.create(name="Terrassa", population=200000, region=r)

    url = reverse("snippets:get-municipality")

    response = client.get(url)

    content = response.json()

    assert content[0]["name"] == ci.name
    assert content[0]["region"] == ci.region.name


@pytest.mark.django_db
def test_get_municipality_CONTENT_TOWN(client):
    c = country.objects.create(name="Spain")
    r = region.objects.create(name="Barcelona", country=c)
    t = town.objects.create(name="Vacarisses", population=2000, region=r)

    url = reverse("snippets:get-municipality")

    response = client.get(url)

    content = response.json()

    assert content[0]["name"] == t.name
    assert content[0]["region"] == t.region.name
