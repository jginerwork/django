import pytest
from django.urls import reverse
from snippets.models import country
import json

@pytest.mark.django_db
def test_country_crud(client):
    url = reverse('snippets:country-list')

    # CREATE
    data = {'name': 'France'}
    response = client.post(url, json.dumps(data), content_type='application/json')
    assert response.status_code == 201
    assert country.objects.count() == 1
    
    c_id = response.json()['id']
    
    # RETRIEVE
    url_detail = reverse('snippets:country-detail', args=[c_id])
    response = client.get(url_detail)
    assert response.status_code == 200
    assert response.json()['name'] == 'France'

    # UPDATE
    data_update = {'name': 'Francia'}
    response = client.put(url_detail, json.dumps(data_update), content_type='application/json')
    assert response.status_code == 200
    assert country.objects.get(id=c_id).name == 'Francia'

    # DELETE
    response = client.delete(url_detail)
    assert response.status_code == 204
    assert country.objects.count() == 0