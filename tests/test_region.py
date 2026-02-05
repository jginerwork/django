import json

import pytest
from django.urls import reverse

from snippets.models import country, region


@pytest.mark.django_db
def test_get_regions_GET_OK(client):
    country_inst = country.objects.create(name="Spain")
    region.objects.create(name="Example1", country=country_inst)
    url = reverse("snippets:region-list")
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_get_regions_GET_CONTENT(client):
    country_inst = country.objects.create(name="Spain")
    region_inst = region.objects.create(name="Example1", country=country_inst)
    url = reverse("snippets:region-list")
    response = client.get(url)
    data = response.json()
    assert len(data["results"]) == 1
    assert data["results"][0]["name"] == region_inst.name
    assert data["results"][0]["country"] == region_inst.country.name


@pytest.mark.django_db
def test_get_regions_GET_EMPTY(client):
    url = reverse("snippets:region-list")
    response = client.get(url)
    data = response.json()
    assert len(data["results"]) == 0
    assert response.status_code == 200


@pytest.mark.django_db
def test_get_regions_POST_OK(client):
    country.objects.create(name="Spain")
    body = {"name": "Example1", "country": "Spain"}
    url = reverse("snippets:region-list")
    response = client.post(url, data=json.dumps(body), content_type="application/json")
    assert response.status_code == 201


@pytest.mark.django_db
def test_get_regions_POST_ERROR(client):
    country.objects.create(name="Spain")
    body = {"hola": "si", "country": "Spain"}
    url = reverse("snippets:region-list")
    response = client.post(url, data=json.dumps(body), content_type="application/json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_get_regions_POST_CONTENT(client):
    country.objects.create(name="Spain")
    body = {"name": "Example1", "country": "Spain"}
    url = reverse("snippets:region-list")
    response = client.post(url, data=json.dumps(body), content_type="application/json")
    data = response.json()
    assert data["name"] == body["name"]
    assert data["country"] == body["country"]
    obj = region.objects.filter(name=data["name"])
    assert len(obj) == 1
    assert obj[0].country.name == data["country"]


# TESTS DE BORRADO MASIVO NO IMPLEMENTADO

"""@pytest.mark.django_db
def test_get_regions_DELETE_OK(client):
    country_inst = country.objects.create(name='Spain')
    region_inst = region.objects.create(name='Example1', country = country_inst)
    url = reverse('snippets:region-list')
    response = client.delete(url)
    assert response.status_code == 200

@pytest.mark.django_db
def test_get_regions_DELETE_CONTENT(client):
    country_inst = country.objects.create(name='Spain')
    region_inst = region.objects.create(name='Example1', country = country_inst)
    url = reverse('snippets:region-list')
    response = client.delete(url)
    inst = region.objects.all()
    assert len(inst) == 0
    inst_country = country.objects.get(name='Spain')
    assert country_inst == inst_country"""


@pytest.mark.django_db
def test_get_region_by_name_GET_OK(client):
    country_inst = country.objects.create(name="Spain")
    region_inst = region.objects.create(name="Example1", country=country_inst)
    url = reverse("snippets:region-detail", args={region_inst.name})
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_get_region_by_name_GET_ERROR(client):
    url = reverse("snippets:region-detail", args={"hola"})
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_get_region_by_name_GET_CONTENT(client):
    country_inst = country.objects.create(name="Spain")
    region_inst = region.objects.create(name="Example1", country=country_inst)
    url = reverse("snippets:region-detail", args=[region_inst.name])
    response = client.get(url)
    data = response.json()
    assert data["name"] == region_inst.name
    assert data["country"] == region_inst.country.name
    obj = region.objects.filter(name="Example1")
    assert len(obj) == 1
    assert obj[0].name == data["name"]
    assert obj[0].country.name == data["country"]


@pytest.mark.django_db
def test_get_region_by_name_DELETE_OK(client):
    country_inst = country.objects.create(name="Spain")
    region_inst = region.objects.create(name="Example1", country=country_inst)
    url = reverse("snippets:region-detail", args=[region_inst.name])
    response = client.delete(url)
    assert response.status_code == 204


@pytest.mark.django_db
def test_get_region_by_name_DELETE_ERROR(client):
    url = reverse("snippets:region-detail", args=["Example1"])
    response = client.delete(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_get_region_by_name_DELETE_CONTENT(client):
    country_inst = country.objects.create(name="Spain")
    region_inst = region.objects.create(name="Example1", country=country_inst)
    url = reverse("snippets:region-detail", args=[region_inst.name])
    client.delete(url)
    inst = region.objects.filter(name=region_inst.name)
    assert len(inst) == 0


@pytest.mark.django_db
def test_get_region_by_name_PUT_OK(client):
    country_inst = country.objects.create(name="Spain")
    region_inst = region.objects.create(name="Example1", country=country_inst)
    url = reverse("snippets:region-detail", args={region_inst.name})
    body = {"name": "exe2", "country": "Spain"}
    response = client.put(url, json.dumps(body), content_type="application/json")
    assert response.status_code == 200


@pytest.mark.django_db
def test_get_region_by_name_PUT_ERROR(client):
    url = reverse("snippets:region-detail", args={"exe1"})
    body = {"name": "exe2", "country": "Spain"}
    response = client.put(url, json.dumps(body), content_type="application/json")
    assert response.status_code == 404


@pytest.mark.django_db
def test_get_region_by_name_PUT_CONTENT(client):
    country_inst = country.objects.create(name="Spain")
    region_inst = region.objects.create(name="Example1", country=country_inst)
    url = reverse("snippets:region-detail", args=[region_inst.name])
    body = {"name": "Exe2", "country": "Spain"}
    response = client.put(url, json.dumps(body), content_type="application/json")
    data = response.json()
    assert data["name"] == body["name"]
    assert data["country"] == body["country"]
    inst = region.objects.filter(name=data["name"])
    assert len(inst) == 1
    assert inst[0].name == data["name"]
    assert inst[0].country.name == data["country"]
    old_inst = region.objects.filter(name=region_inst.name)
    assert len(old_inst) == 0


@pytest.mark.django_db
def test_get_region_POST_CAPITALIZE(client):
    c = country.objects.create(name="Spain")

    url = reverse("snippets:region-list")

    body = {"name": "exe2", "country": c.name}

    response = client.post(url, json.dumps(body), content_type="application/json")
    assert response.status_code == 201
    assert response.json()["name"] == body["name"].title()


@pytest.mark.django_db
def test_get_region_DELETE_CASCADE(client):
    c = country.objects.create(name="Spain")
    region.objects.create(name="Region1", country=c)

    assert region.objects.count() == 1

    c.delete()

    assert region.objects.count() == 0
