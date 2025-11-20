#from django.shortcuts import render
#from django.http import HttpResponse, JsonResponse #devolver respuesta HTT básica, devolver datos en JSON
#from django.views.decorators.csrf import csrf_exempt #desactiva temporalment CSRF per una vista
#from rest_framework.parsers import JSONParser #converteix de JSON a un diccionari Python (que es put utilitzar amb serializer)
#from rest_framework import status
#from rest_framework.decorators import api_view
#from rest_framework.response import Response
from snippets.models import Snippet #model definit anteriornment
from snippets.serializers import SnippetSerializer, UserSerializer #serializer que hem creat
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins
from rest_framework import generics, permissions
from django.contrib.auth.models import User
from snippets.serializers import UserSerializer
from snippets.permissions import IsOwnerOrReadOnly
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import renderers
from rest_framework import viewsets



# Create your views here.
"""
@csrf_exempt #desactiva csrf
def snippet_list(request): #vista basada en funció
    """
    #List all code snippets, or create a new snippet.
"""
    if request.method == "GET": #quan el client fa un get
        snippets = Snippet.objects.all() #agafa tots els clients de la bd
        serializer = SnippetSerializer(snippets, many=True) # els converteix a format json
        return JsonResponse(serializer.data, safe=False) # retorna les dades en format json

    elif request.method == "POST": #quan el client crea un snippet
        data = JSONParser().parse(request) #converteix petició JSON a diccionari Python
        serializer = SnippetSerializer(data=data) #prepara dades per validar
        if serializer.is_valid(): #valida que les dades cumpleixin amb els requisits del serializer
            serializer.save() #guarda a bd
            return JsonResponse(serializer.data, status=201) #retorna snippet recen creat
        return JsonResponse(serializer.errors, status=400) #retorna error si les dades no són vàlides

@csrf_exempt
def snippet_detail(request, pk): #per mètodes que requereixen l'id (primary key)
    """
    #Retrieve, update or delete a code snippet.
"""
    try: #intenta obtenir snipped amb pk, si no existeix salta error
        snippet = Snippet.objects.get(pk=pk)
    except Snippet.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == "GET": #converteix snippet a JSON i ho retorna
        serializer = SnippetSerializer(snippet)
        return JsonResponse(serializer.data)

    elif request.method == "PUT":
        data = JSONParser().parse(request) #converteix JSON a diccionari
        serializer = SnippetSerializer(snippet, data=data) #prepara dades per actualitzar snippet
        if serializer.is_valid(): #valida dades
            serializer.save() # guarda bd
            return JsonResponse(serializer.data) #retorna dades
        return JsonResponse(serializer.errors, status=400) #si no es validen les dades salta error

    elif request.method == "DELETE":
        snippet.delete() #borra snippet
        return HttpResponse(status=204)
"""

"""
#function based views
@api_view(["GET", "POST"]) #view amb els components de REST framework
def snippet_list(request, format=None):
    """
    #List all code snippets, or create a new snippet.
"""
    if request.method == "GET":
        snippets = Snippet.objects.all()
        serializer = SnippetSerializer(snippets, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = SnippetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET", "PUT", "DELETE"]) #view amb els components de REST framework
def snippet_detail(request, pk, format=None):
    """
    #Retrieve, update or delete a code snippet.
"""
    try:
        snippet = Snippet.objects.get(pk=pk)
    except Snippet.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = SnippetSerializer(snippet)
        return Response(serializer.data)

    elif request.method == "PUT":
        serializer = SnippetSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

"""
#ja no cal que ens fixem en el format de les respostes ja que request.data accepta JSON i altres formats

"""
class SnippetList(APIView):

    #List all snippets, or create a new snippet.

    def get(self, request, format=None):
        snippets = Snippet.objects.all()
        serializer = SnippetSerializer(snippets, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = SnippetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SnippetDetail(APIView):

    #Retrieve, update or delete a snippet instance.

    def get_object(self, pk):
        try:
            return Snippet.objects.get(pk=pk)
        except Snippet.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = SnippetSerializer(snippet)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = SnippetSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        snippet = self.get_object(pk)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
"""

"""
class SnippetList(
    mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView
):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class SnippetDetail(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView,
):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

"""
#views
"""
class SnippetList(generics.ListCreateAPIView): #el que apareix sense espacificar id
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    def perform_create(self, serializer): #executada automàticament al fer un post
        serializer.save(owner=self.request.user) #afegeix usuari com a owner
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

# noramlement, una view (al rebre un post) valida el serializer, si es vàlid crida self.perform_create(serializer)
# i per defecte fa serializer.save(). Nosaltres volem sobreescriure aquesta funció i afegir al camp owner
# l'usuari que fa la petició

class SnippetDetail(generics.RetrieveUpdateDestroyAPIView): #el que apareix una vegada hem especificat l'id
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    

class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
"""

@api_view(["GET"])
def api_root(request, format=None):
    return Response(
        {
            "users": reverse("user-list", request=request, format=format), #funcio per retornar urls
            "snippets": reverse("snippet-list", request=request, format=format),
        }
    )

class SnippetHighlight(generics.GenericAPIView):
    queryset = Snippet.objects.all()
    renderer_classes = [renderers.StaticHTMLRenderer]

    def get(self, request, *args, **kwargs):
        snippet = self.get_object()
        return Response(snippet.highlighted)

#view sets
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer



class SnippetViewSet(viewsets.ModelViewSet):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        snippet = self.get_object()
        return Response(snippet.highlighted)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
