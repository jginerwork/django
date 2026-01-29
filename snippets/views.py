#from django.shortcuts import render
#from django.http import HttpResponse, JsonResponse #devolver respuesta HTT básica, devolver datos en JSON
#from django.views.decorators.csrf import csrf_exempt #desactiva temporalment CSRF per una vista
#from rest_framework.parsers import JSONParser #converteix de JSON a un diccionari Python (que es put utilitzar amb serializer)
#from rest_framework import status
#from rest_framework.decorators import api_view
#from rest_framework.response import Response
from snippets.models import Snippet, book, editorial, opinion, country, region, municipality, town, city, Genre#, company #model definit anteriornment
from snippets.serializers import BookSerializer, SnippetSerializer, UserSerializer #serializer que hem creat
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
from django.db import connection
from .serializers import EditorialSerializer, UserRegistrationSerializer, OpinionSerializer, CountrySerializer, RegionSerializer, MunicipalitySerializer, CitySerializer, TownSerializer, GenreSerializer#, CompanySerializer
from rest_framework.decorators import throttle_classes
from rest_framework.throttling import UserRateThrottle
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic.list import MultipleObjectMixin
from django.db.models import Q
from django.db.models import Count  # <--- Asegúrate de tener este import arriba

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
    queryset = User.objects.prefetch_related("snippets").all()
    serializer_class = UserSerializer

class SnippetViewSet(viewsets.ModelViewSet):
    queryset = Snippet.objects.select_related("owner").all() #agafa directament l'owner de la base de dades
    serializer_class = SnippetSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]


    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        snippet = self.get_object()
        return Response(snippet.highlighted)
    

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user) #save s'utilitza per retornar una instància

    def get_queryset(self):

        if self.request.user.is_authenticated:
            return Snippet.objects.filter(Q(draft=True) & Q(owner=self.request.user) | Q(draft=False))
        return Snippet.objects.filter(draft=False)
    
    @action(detail=True, methods=['post'])
    def publish(self, request, *args, **kwargs):
        snippet = self.get_object()
        if self.request.user == snippet.owner:
            snippet.draft = False
            snippet.save()
            return Response(self.get_serializer(snippet).data)
        return Response({'error': 'You are not the owner of this snippet'}, status = 403)
    
    @action(detail=True, methods=['post', 'get'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, *args, **kwargs):
        snippet = self.get_object()
        if snippet.like.filter(id=self.request.user.id).exists():
            snippet.like.remove(self.request.user)
            return Response(status=204)
        else:
            snippet.like.add(self.request.user)
            return Response(status=204)
        
    @action(detail=False, permission_classes=[permissions.AllowAny])
    def list_popular(self, request, *args, **kwargs):
        snippets = Snippet.objects.filter(draft=False).select_related('owner').annotate(total_likes=Count('like')).order_by("-total_likes")
        serializer = self.get_serializer(snippets, many=True)
        return Response(serializer.data)


class BookViewSet(viewsets.ModelViewSet):
    queryset = book.objects.select_related("editorial").all() #afaga directament tots els snippets corresponents de la base de dades
    serializer_class = BookSerializer
   

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer 

class EditorialViewSet(viewsets.ModelViewSet):
    queryset = editorial.objects.all()
    serializer_class = EditorialSerializer

class OpinionViewSet(viewsets.ModelViewSet):
    queryset = opinion.objects.select_related("book").all()
    serializer_class = OpinionSerializer
    
    def perform_create(self, serializer):
        serializer.save(autor=self.request.user)

class CountryViewSet(viewsets.ModelViewSet):
    queryset = country.objects.all()
    serializer_class = CountrySerializer

"""class CompanyViewSet(viewsets.ModelViewSet):
    queryset = company.objects.all()
    serializer_class = CompanySerializer"""

class OncePerDayUserThrottle(UserRateThrottle):
    rate = '1/day'

@api_view(['GET'])
@throttle_classes([OncePerDayUserThrottle])
def view(request):
    return Response({"message": "Hello for today! See you tomorrow"})

"""
class RegionsList(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = region.objects.all().order_by('id')
    serializer_class = RegionSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        all_regions = self.get_queryset()
        all_regions.delete()

        return JsonResponse(
            {"Message": "Regions deleted"},
            status = status.HTTP_200_OK
        )
"""

         


#hi ha varies convinacions de mixins implementades per generics. Mirar documentació abans de triar quina utilitzar
#es pot crear classes Mixin per implementar funcionalitat diferent a la estàndard, després la funció es crida igual que s'utilitzaria un mixin precreat
    
"""
class RegionDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    queryset = region.objects.all()
    serializer_class = RegionSerializer

    lookup_field= 'name'

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
"""

"""class MunicipalityList(mixins.ListModelMixin, generics.GenericAPIView):
    queryset = municipality.objects.all()
    serializer_class = MunicipalitySerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)"""

class CapitalizeMixin:
    def perform_create(self, serializer): #metodo que se ejecuta automaticamente al hacer un post
        self._capitalize_fields(serializer) #llamamos nueva función
        super().perform_create(serializer) #llamamos al metodo original (para que se guarde en db)

    def perform_update(self, serializer): #metodo que se ejecuta automaticamente al hacer put o patch
        self._capitalize_fields(serializer) #llamamos nueva función
        super().perform_update(serializer) #llamamos al metodo original

    def _capitalize_fields(self, serializer): #función auxiliar privada (por _ inicial) para mayusculas
        target_fields = ['name', 'title'] #nombres de los campos que queremos transformar

        for field in target_fields: #bucle per revisr cada camp
            if field in serializer.validated_data: #entra al if si l'usuari ha enviat el camp field
                value = serializer.validated_data[field] #value = valor actual del camp
                if isinstance(value, str): #verifica que el valor sigui text
                    serializer.validated_data[field] = value.title() #canvia el valor del camp per el que ja hi havia en majuscules
        
        sentence_fields = ['description']

        for field in sentence_fields:
            if field in serializer.validated_data:
                value = serializer.validated_data[field]
                if isinstance(value, str):
                    serializer.validated_data[field] = value.capitalize()
                    

"""class RegionDetail(CapitalizeMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = region.objects.all()
    serializer_class = RegionSerializer
    lookup_field = 'name'
    
class RegionsList(CapitalizeMixin, generics.ListCreateAPIView):
    queryset = region.objects.all().order_by('id')
    serializer_class = RegionSerializer"""

class RegionViewSet(CapitalizeMixin, viewsets.ModelViewSet):
    queryset = region.objects.all().order_by('id')
    serializer_class = RegionSerializer
    lookup_field = 'name'


class MunicipalityList(MultipleObjectMixin, View):
    queryset = municipality.objects.all()

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()  

        serializer = MunicipalitySerializer(self.object_list, many = True)  
        return JsonResponse(serializer.data, safe=False)


class TownList(CapitalizeMixin, generics.ListCreateAPIView):
    queryset = town.objects.all().order_by('id')
    serializer_class = TownSerializer

class CityList(CapitalizeMixin, generics.ListCreateAPIView):
    queryset = city.objects.all().order_by('id')
    serializer_class = CitySerializer

class GenreViewSet(CapitalizeMixin, viewsets.ModelViewSet):
    queryset = Genre.objects.all().order_by('id')
    serializer_class = GenreSerializer
    lookup_field = 'name'