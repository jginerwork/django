# from django.shortcuts import render
# from django.http import HttpResponse, JsonResponse #devolver respuesta HTT básica, devolver datos en JSON
# from django.views.decorators.csrf import csrf_exempt #desactiva temporalment CSRF per una vista
# from rest_framework.parsers import JSONParser #converteix de JSON a un diccionari Python (que es put utilitzar amb serializer)
# from rest_framework import status
# from rest_framework.decorators import api_view
# from rest_framework.response import Response

from .serializers import CitySerializer  # , CompanySerializer
from .serializers import (
    CommentSerializer,
    CountrySerializer,
    EditorialSerializer,
    GenreSerializer,
    MunicipalitySerializer,
    NotificationSerializer,
    OpinionSerializer,
    RegionSerializer,
    TownSerializer,
    UserRegistrationSerializer,
)
from django.contrib.auth.models import User
from django.db.models import Count  # <--- Asegúrate de tener este import arriba
from django.db.models import Q
from django.http import JsonResponse
from django.views import View
from django.views.generic.list import MultipleObjectMixin
from rest_framework import generics, mixins, permissions, renderers, viewsets
from rest_framework.decorators import action, api_view, throttle_classes
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.throttling import UserRateThrottle
from snippets.models import Comment  # , company #model definit anteriornment
from snippets.models import (
    Following,
    Genre,
    Notification,
    Snippet,
    book,
    city,
    country,
    editorial,
    municipality,
    opinion,
    region,
    town,
)
from snippets.permissions import IsOwnerOrReadOnly
from snippets.serializers import BookSerializer  # serializer que hem creat
from snippets.serializers import SnippetSerializer, UserSerializer


@api_view(["GET"])
def api_root(request, format=None):
    return Response(
        {
            "users": reverse(
                "user-list", request=request, format=format
            ),  # funcio per retornar urls
            "snippets": reverse("snippet-list", request=request, format=format),
        }
    )


class SnippetHighlight(generics.GenericAPIView):
    queryset = Snippet.objects.all()
    renderer_classes = [renderers.StaticHTMLRenderer]

    def get(self, request, *args, **kwargs):
        snippet = self.get_object()
        return Response(snippet.highlighted)


# view sets
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.prefetch_related("snippets").all()
    serializer_class = UserSerializer

    @action(
        detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def follow(self, request, *args, **kwargs):
        connections = Following.objects.filter(
            user_follower=request.user, user_followed=self.get_object()
        )
        if connections.exists():
            connections.delete()
            return Response(status=204)
        Following.objects.create(
            user_follower=request.user, user_followed=self.get_object()
        )
        return Response(status=201)


class SnippetViewSet(viewsets.ModelViewSet):
    queryset = Snippet.objects.select_related(
        "owner"
    ).all()  # agafa directament l'owner de la base de dades
    serializer_class = SnippetSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        snippet = self.get_object()
        return Response(snippet.highlighted)

    def perform_create(self, serializer):
        serializer.save(
            owner=self.request.user
        )  # save s'utilitza per retornar una instància

    def perform_update(self, serializer):
        snippet = self.get_object()
        if snippet.draft:
            return super().perform_update(serializer)
        raise ValidationError({"error": "Snippet is published"})

    def get_queryset(self):

        if self.request.user.is_authenticated:
            return Snippet.objects.filter(
                Q(draft=True) & Q(owner=self.request.user) | Q(draft=False)
            )
        return Snippet.objects.filter(draft=False)

    def get_serializer_class(self):
        # Si la acción es 'add_comment', usa el serializer de comentarios
        if self.action == "add_comment":
            return CommentSerializer
        # Para todo lo demás (list, retrieve, create...), usa el de Snippets
        return SnippetSerializer

    @action(detail=True, methods=["post", "get"])
    def publish(self, request, *args, **kwargs):
        snippet = self.get_object()
        if self.request.user == snippet.owner:
            snippet.draft = False
            snippet.save()
            return Response(self.get_serializer(snippet).data)
        return Response({"error": "You are not the owner of this snippet"}, status=403)

    @action(
        detail=True,
        methods=["post", "get"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def like(self, request, *args, **kwargs):
        snippet = self.get_object()
        if snippet.draft:
            return Response({"error": "You can't like a draft"}, status=400)
        if snippet.like.filter(id=self.request.user.id).exists():
            snippet.like.remove(self.request.user)
            return Response(status=204)
        else:
            snippet.like.add(self.request.user)
            return Response(status=204)

    @action(detail=False, permission_classes=[permissions.AllowAny])
    def list_popular(self, request, *args, **kwargs):
        snippets = (
            Snippet.objects.filter(draft=False)
            .select_related("owner")
            .annotate(total_likes=Count("like"))
            .order_by("-total_likes")
        )
        serializer = self.get_serializer(snippets, many=True)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["post", "get"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def add_comment(self, request, pk=None):
        if request.method == "GET":
            serializer = self.get_serializer()
            return Response(serializer.data)

        # Si es POST, procesamos los datos
        snippet = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save(owner=request.user, snippet=snippet)
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def filter_following(self, request, *args, **kwargs):
        users_followed = User.objects.filter(followed__user_follower=request.user)
        snippets = Snippet.objects.filter(owner__in=users_followed)
        serializer = self.get_serializer(snippets, many=True)
        return Response(data=serializer.data, status=200)


class BookViewSet(viewsets.ModelViewSet):
    queryset = book.objects.select_related(
        "editorial"
    ).all()  # afaga directament tots els snippets corresponents de la base de dades
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
        serializer.save(author=self.request.user)


class CountryViewSet(viewsets.ModelViewSet):
    queryset = country.objects.all()
    serializer_class = CountrySerializer


"""class CompanyViewSet(viewsets.ModelViewSet):
    queryset = company.objects.all()
    serializer_class = CompanySerializer"""


class OncePerDayUserThrottle(UserRateThrottle):
    rate = "1/day"


@api_view(["GET"])
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


# hi ha varies convinacions de mixins implementades per generics. Mirar documentació abans de triar quina utilitzar
# es pot crear classes Mixin per implementar funcionalitat diferent a la estàndard, després la funció es crida igual que s'utilitzaria un mixin precreat

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
    def perform_create(
        self, serializer
    ):  # metodo que se ejecuta automaticamente al hacer un post
        self._capitalize_fields(serializer)  # llamamos nueva función
        super().perform_create(
            serializer
        )  # llamamos al metodo original (para que se guarde en db)

    def perform_update(
        self, serializer
    ):  # metodo que se ejecuta automaticamente al hacer put o patch
        self._capitalize_fields(serializer)  # llamamos nueva función
        super().perform_update(serializer)  # llamamos al metodo original

    def _capitalize_fields(
        self, serializer
    ):  # función auxiliar privada (por _ inicial) para mayusculas
        target_fields = [
            "name",
            "title",
        ]  # nombres de los campos que queremos transformar

        for field in target_fields:  # bucle per revisr cada camp
            if (
                field in serializer.validated_data
            ):  # entra al if si l'usuari ha enviat el camp field
                value = serializer.validated_data[
                    field
                ]  # value = valor actual del camp
                if isinstance(value, str):  # verifica que el valor sigui text
                    serializer.validated_data[field] = (
                        value.title()
                    )  # canvia el valor del camp per el que ja hi havia en majuscules

        sentence_fields = ["description"]

        for field in sentence_fields:
            if field in serializer.validated_data:
                value = serializer.validated_data[field]
                if isinstance(value, str):
                    serializer.validated_data[field] = value.capitalize()


class RegionViewSet(CapitalizeMixin, viewsets.ModelViewSet):
    queryset = region.objects.all().order_by("id")
    serializer_class = RegionSerializer
    lookup_field = "name"


class MunicipalityList(MultipleObjectMixin, View):
    queryset = municipality.objects.all()

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()

        serializer = MunicipalitySerializer(self.object_list, many=True)
        return JsonResponse(serializer.data, safe=False)


class TownList(CapitalizeMixin, generics.ListCreateAPIView):
    queryset = town.objects.all().order_by("id")
    serializer_class = TownSerializer


class CityList(CapitalizeMixin, generics.ListCreateAPIView):
    queryset = city.objects.all().order_by("id")
    serializer_class = CitySerializer


class GenreViewSet(CapitalizeMixin, viewsets.ModelViewSet):
    queryset = Genre.objects.all().order_by("id")
    serializer_class = GenreSerializer
    lookup_field = "name"


class CommentViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    @action(
        detail=True,
        methods=["post", "get"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def like(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.like.filter(id=self.request.user.id).exists():
            comment.like.remove(self.request.user)
            return Response(status=204)
        else:
            comment.like.add(self.request.user)
            return Response(status=204)

    @action(
        detail=True,
        methods=["post", "get"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def add_comment(self, request, pk=None):
        parent_comment = self.get_object()
        if request.method == "GET":
            serializer = self.get_serializer()
            return Response(serializer.data)

        # Si es POST, procesamos los datos
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save(
                owner=request.user,
                parent=parent_comment,
                snippet=parent_comment.snippet,
            )
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)
