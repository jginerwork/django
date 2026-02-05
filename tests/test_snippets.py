import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from snippets.models import Snippet
import json

# --- Fixtures (Datos de prueba reutilizables) ---

@pytest.fixture
def user_owner(db):
    return User.objects.create_user(username='owner', password='password123')

@pytest.fixture
def user_other(db):
    return User.objects.create_user(username='other', password='password123')

@pytest.fixture
def snippet_public(db, user_owner):
    return Snippet.objects.create(
        owner=user_owner, 
        title="Public Snippet", 
        code="print('hello')", 
        draft=False
    )

@pytest.fixture
def snippet_draft(db, user_owner):
    return Snippet.objects.create(
        owner=user_owner, 
        title="Draft Snippet", 
        code="print('secret')", 
        draft=True
    )

# --- Tests de Creación y Listado ---

@pytest.mark.django_db
def test_create_snippet_authenticated(client, user_owner):
    """
    Test para verificar que un usuario logueado puede crear un snippet.
    Se verifica que el 'owner' se asigna automáticamente en perform_create.
    """
    client.force_login(user_owner)
    url = reverse('snippets:snippet-list')
    data = {
        'title': 'New Python Code',
        'code': 'def foo(): pass',
        'language': 'python',
        'style': 'friendly'
    }

    response = client.post(url, data=json.dumps(data), content_type='application/json')
    
    assert response.status_code == 201
    assert response.json()['title'] == 'New Python Code'
    assert response.json()['owner'] == f'http://testserver/users/{user_owner.id}/' # HyperlinkedRelatedField
    # Por defecto draft debe ser True según el modelo
    assert Snippet.objects.get(title='New Python Code').draft is True 

@pytest.mark.django_db
def test_create_snippet_unauthenticated(client):
    """
    Test para verificar que un usuario anónimo NO puede crear snippets.
    Permiso: IsAuthenticatedOrReadOnly.
    """
    url = reverse('snippets:snippet-list')
    data = {'code': 'print("fail")'}
    response = client.post(url, data, content_type='application/json')
    assert response.status_code == 403

# --- Tests de Visibilidad (get_queryset) ---

@pytest.mark.django_db
def test_list_snippets_visibility(client, user_owner, user_other):
    """
    Prueba compleja para el get_queryset:
    - Debe verse lo público de todos.
    - Debe verse lo borrador (draft) SOLO si es mío.
    - NO debe verse lo borrador ajeno.
    """
    # 1. Crear datos
    # Público del Owner
    s1 = Snippet.objects.create(owner=user_owner, title="Public Owner", code="x", draft=False)
    # Borrador del Owner
    s2 = Snippet.objects.create(owner=user_owner, title="Draft Owner", code="x", draft=True)
    # Borrador de Otro usuario
    s3 = Snippet.objects.create(owner=user_other, title="Draft Other", code="x", draft=True)

    # 2. Loguearse como 'user_owner'
    client.force_login(user_owner)
    url = reverse('snippets:snippet-list')
    response = client.get(url)
    
    results = response.json()['results']
    titles = [s['title'] for s in results]

    # 3. Verificaciones
    assert "Public Owner" in titles
    assert "Draft Owner" in titles
    assert "Draft Other" not in titles # El filtro debe ocultar el borrador ajeno
    assert len(results) == 2

@pytest.mark.django_db
def test_retrieve_snippet_draft_permission(client, user_other, snippet_draft):
    """
    Intento de acceder directamente por ID a un borrador ajeno.
    Debe dar 404 porque el get_queryset lo filtra antes de comprobar permisos.
    """
    client.force_login(user_other)
    url = reverse('snippets:snippet-detail', args=[snippet_draft.id])
    response = client.get(url)
    assert response.status_code == 404

# --- Tests de Acciones Personalizadas (@action) ---

@pytest.mark.django_db
def test_action_publish_owner(client, user_owner, snippet_draft):
    """
    El dueño publica su borrador.
    """
    client.force_login(user_owner)
    url = reverse('snippets:snippet-publish', args=[snippet_draft.id])
    
    response = client.post(url)
    
    snippet_draft.refresh_from_db()
    
    assert response.status_code == 200
    assert snippet_draft.draft is False # Debe haber cambiado en DB

@pytest.mark.django_db
def test_action_publish_not_owner(client, user_other, snippet_draft):
    """
    Otro usuario intenta publicar un borrador ajeno.
    Nota: Como 'snippet_draft' es draft=True, el get_queryset lo ocultará al 'user_other' 
    dando un 404. Para probar el 403 explícito de la vista 'publish', 
    necesitamos un snippet que user_other pueda VER pero no editar (draft=False).
    """
    # Hacemos el snippet visible (publico) pero intentamos llamar a publish igual
    snippet_draft.draft = False 
    snippet_draft.save()
    
    client.force_login(user_other)
    url = reverse('snippets:snippet-publish', args=[snippet_draft.id])
    
    response = client.post(url)
    
    assert response.status_code == 403
    # CAMBIO: DRF devuelve 'detail', no 'error' cuando bloquea por permisos globales
    assert 'detail' in response.json()

@pytest.mark.django_db
def test_action_like(client, user_other, snippet_public):
    """
    Test de dar like y quitar like.
    Verifica también el campo 'likes_count' del serializer.
    """
    client.force_login(user_other)
    url_like = reverse('snippets:snippet-like', args=[snippet_public.id])
    url_detail = reverse('snippets:snippet-detail', args=[snippet_public.id])

    # 1. Dar Like
    response = client.post(url_like)
    assert response.status_code == 204 # Según tu views.py retorna 204
    assert snippet_public.like.count() == 1

    # 2. Verificar likes_count en el detalle (Serializer field)
    resp_detail = client.get(url_detail)
    assert resp_detail.json()['likes_count'] == 1

    # 3. Quitar Like (Toggle)
    response = client.post(url_like)
    assert response.status_code == 204
    assert snippet_public.like.count() == 0

@pytest.mark.django_db
def test_action_highlight(client, user_owner, snippet_public):
    """
    Test para renderizado HTML (highlight).
    """
    client.force_login(user_owner)
    url = reverse('snippets:snippet-highlight', args=[snippet_public.id])
    
    response = client.get(url)
    
    assert response.status_code == 200
    # Verifica que devuelve HTML (buscando etiquetas generadas por pygments)
    assert '<div' in str(response.content) 
    assert 'class="highlight"' in str(response.content)

# --- Tests de Permisos de Edición/Borrado ---

@pytest.mark.django_db
def test_update_snippet_permission(client, user_owner, user_other, snippet_public):
    """
    Verifica IsOwnerOrReadOnly:
    - Dueño puede editar (PUT).
    - Otro usuario no puede editar (403).
    """
    url = reverse('snippets:snippet-detail', args=[snippet_public.id])
    
    # Datos completos para el PUT
    data = {
        'title': 'Updated Title',
        'code': 'updated',
        'language': 'python',
        'style': 'friendly',
        'linenos': False,
        'draft': False, 
        # 'fuente': None # Ya no hace falta, pero si lo pones no estorba
    }

    # 1. Intento de update por otro usuario (Debe dar 403 porque es público)
    client.force_login(user_other)
    response = client.put(url, json.dumps(data), content_type='application/json')
    assert response.status_code == 403

    # 2. Update por el dueño
    client.force_login(user_owner)
    
    # --- PASO CRUCIAL: Convertir a borrador para permitir la edición ---
    snippet_public.draft = True
    snippet_public.save()
    # ------------------------------------------------------------------

    response = client.put(url, json.dumps(data), content_type='application/json')

    assert response.status_code == 200
    assert response.json()['title'] == 'Updated Title'