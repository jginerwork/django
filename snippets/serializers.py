from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from snippets.models import (
    Comment,
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

# los serializers permiten convertir modelos de django a json
"""
class SnippetSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True) #read_only perquè no es pot enviar al crear un snippet
    title = serializers.CharField(required=False, allow_blank=True, max_length=100)
    code = serializers.CharField(style={"base_template": "textarea.html"}) #codi renderitzat en fomat textarea
    linenos = serializers.BooleanField(required=False) #bolea per tiar si volem veure els numeros de linea (al codi)
    language = serializers.ChoiceField(choices=LANGUAGE_CHOICES, default="python") #llenguatge delsnippet
    style = serializers.ChoiceField(choices=STYLE_CHOICES, default="friendly") #Estil de resaltat de codi

    def create(self, validated_data): #crea un nou snippet (post)

        #Create and return a new `Snippet` instance, given the validated data.

        return Snippet.objects.create(**validated_data) #crea l'objecte a la base de dades

    def update(self, instance, validated_data):

        #Update and return an existing `Snippet` instance, given the validated data.

        instance.title = validated_data.get("title", instance.title) #actualitza el camp title si hi ha canvis
        instance.code = validated_data.get("code", instance.code)
        instance.linenos = validated_data.get("linenos", instance.linenos)
        instance.language = validated_data.get("language", instance.language)
        instance.style = validated_data.get("style", instance.style)
        instance.save() #guarda els canvis a la base de dades
        return instance
"""
# relacions utilitzant primary keys
"""
class SnippetSerializer(serializers.ModelSerializer): #shortcut per serializer classes
    owner = serializers.ReadOnlyField(source="owner.username") #també podriem utilitzar CharField(read_only=True)
    class Meta:
        model = Snippet
        fields = ["id", "title", "code", "linenos", "language", "style", "owner"]


#representar usuarios junto a los snippets que les pertenecen
#user.snippets.all() permet accedir als snippets que pertanyen a un usuari
class UserSerializer(serializers.ModelSerializer):
    snippets = serializers.PrimaryKeyRelatedField( #representa la relacion mostrando las primary keys
        many=True, queryset=Snippet.objects.all() # 1 a muchos i campo escribible (se pueden asignar snippets a usuarios)
    ) #define campo adicional dentro de users para la relacion de estos con snippet

    class Meta:
        model = User
        fields = ["id", "username", "snippets"]
"""


class CommentSerializer(serializers.ModelSerializer):
    likes_count = serializers.IntegerField(source="like.count", read_only=True)
    owner = serializers.ReadOnlyField(source="owner.username")
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ["text", "owner", "likes_count", "id", "replies"]

    def get_replies(self, obj):
        if obj.replies.exists():
            # Se llama a sí mismo (recursividad) para serializar los hijos
            return CommentSerializer(
                obj.replies.all(), many=True, context=self.context
            ).data
        return []


# relacions utilitzant hyperlinking
# no inclueix l'id per defecte, sinó que inclueix un camp url
class SnippetSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.HyperlinkedRelatedField(
        read_only=True, view_name="snippets:user-detail"
    )
    highlight = serializers.HyperlinkedIdentityField(
        view_name="snippets:snippet-highlight", format="html"
    )
    fuente = serializers.HyperlinkedRelatedField(
        queryset=book.objects.all(),
        read_only=False,
        view_name="snippets:book-detail",
        required=False,
        allow_null=True,
    )
    likes_count = serializers.IntegerField(source="like.count", read_only=True)
    comments = CommentSerializer(many=True, read_only=True, default=None)

    class Meta:
        model = Snippet
        fields = [
            "url",
            "id",
            "highlight",
            "owner",
            "title",
            "code",
            "linenos",
            "language",
            "style",
            "fuente",
            "draft",
            "likes_count",
            "comments",
        ]

        extra_kwargs = {"url": {"view_name": "snippets:snippet-detail"}}


class UserSerializer(serializers.HyperlinkedModelSerializer):
    snippets = serializers.HyperlinkedRelatedField(
        many=True, view_name="snippets:snippet-detail", read_only=True
    )
    followers = serializers.IntegerField(source="followed.count", read_only=True)

    class Meta:
        model = User
        fields = ["url", "id", "username", "snippets", "followers"]
        extra_kwargs = {"url": {"view_name": "snippets:user-detail"}}


class BookSerializer(serializers.HyperlinkedModelSerializer):
    snippets = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name="snippets:snippet-detail"
    )
    author = serializers.HyperlinkedRelatedField(
        queryset=User.objects.all(), read_only=False, view_name="snippets:user-detail"
    )
    editorial = serializers.HyperlinkedRelatedField(
        queryset=editorial.objects.all(), view_name="snippets:editorial-detail"
    )
    opinions = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name="snippets:opinion-detail"
    )

    class Meta:
        model = book
        fields = ["url", "id", "title", "snippets", "author", "editorial", "opinions"]
        extra_kwargs = {"url": {"view_name": "snippets:book-detail"}}


class UserRegistrationSerializer(serializers.ModelSerializer):  # model serializer:
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "first_name", "last_name"]

    def create(
        self, validated_data
    ):  # per utilitzar validated_data necessitem o un create o un update
        user = User.objects.create_user(
            username=validated_data[
                "username"
            ],  # o retornen les dades validades o salta excepció
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        return user


class EditorialSerializer(serializers.HyperlinkedModelSerializer):
    books = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name="snippets:book-detail"
    )

    class Meta:
        model = editorial
        fields = ["url", "id", "name", "books", "email", "countries"]
        extra_kwargs = {"url": {"view_name": "snippets:editorial-detail"}}


class OpinionSerializer(serializers.HyperlinkedModelSerializer):
    book = serializers.HyperlinkedRelatedField(
        queryset=book.objects.all(), view_name="snippets:book-detail"
    )
    author = serializers.ReadOnlyField(source="author.username")

    class Meta:
        model = opinion
        fields = ["url", "id", "title", "text", "rating", "author", "book", "date"]
        extra_kwargs = {"url": {"view_name": "snippets:opinion-detail"}}


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = country
        fields = ["id", "name"]


class RegionSerializer(serializers.ModelSerializer):
    country = serializers.SlugRelatedField(
        queryset=country.objects.all(), slug_field="name"
    )

    class Meta:
        model = region
        fields = "__all__"


class MunicipalitySerializer(serializers.ModelSerializer):
    region = serializers.StringRelatedField()

    class Meta:
        model = municipality
        fields = "__all__"


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = city
        fields = "__all__"
        validators = [
            UniqueTogetherValidator(
                queryset=municipality.objects.all(), fields=["name", "region"]
            )
        ]


class TownSerializer(serializers.ModelSerializer):
    class Meta:
        model = town
        fields = "__all__"
        validators = [
            UniqueTogetherValidator(
                queryset=municipality.objects.all(), fields=["name", "region"]
            )
        ]


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = "__all__"


class NotificationSerializer(serializers.ModelSerializer):
    actor = serializers.ReadOnlyField(source="actor.username")
    target = serializers.StringRelatedField()

    class Meta:
        model = Notification
        fields = ["id", "actor", "verb", "target", "created", "read"]
