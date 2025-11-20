from rest_framework import serializers
from snippets.models import Snippet, LANGUAGE_CHOICES, STYLE_CHOICES #llistes que hem generat abans
from django.contrib.auth.models import User



#los serializers permiten convertir modelos de django a json
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
#relacions utilitzant primary keys
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
#relacions utilitzant hyperlinking
#no inclueix l'id per defecte, sinó que inclueix un camp url
class SnippetSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")
    highlight = serializers.HyperlinkedIdentityField(
        view_name="snippet-highlight", format="html"
    )

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
        ]


class UserSerializer(serializers.HyperlinkedModelSerializer):
    snippets = serializers.HyperlinkedRelatedField(
        many=True, view_name="snippet-detail", read_only=True
    )

    class Meta:
        model = User
        fields = ["url", "id", "username", "snippets"]