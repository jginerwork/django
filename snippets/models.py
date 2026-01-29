from django.db import models
#pygments: libreria de resaltado de sintaxis
from pygments.lexers import get_all_lexers #devulve todos los lenguajes de programación reconocidos por pygments
from pygments.styles import get_all_styles #devuelve todos los estilos de colores utilizados por pygments para resaltar codigo
from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import HtmlFormatter
from pygments import highlight
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

LEXERS = [item for item in get_all_lexers() if item[1]] #devuelve los lenguajes con un alias (?)
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS]) #devuelve lista de tuplas (alias_lenguaje, nombre_lenguaje)
STYLE_CHOICES = sorted([(item, item) for item in get_all_styles()]) #lista tuplas estilos disponibles

#util para en un formulario desplegar select de todos los lenguajes y estilos disponibles

#model methods intended to act on a particular model instance, to act on the whole table use manager methods
# hi ha bastants mètode de models definits automàticament, si els volem canviar els hem de tornar
# a definir. un d'ells és __str__ que per defecte retorna l'id de la instància
# un altre mètode predefinit és get_absolute_url() utilitzat per a trobar les urls
#també hi ha save() i delete() -> accedir al de la superclasse utilitzant super().save() o super().delete()


#document models.py utilitzat per fer els models de les classes
class Snippet(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=True, default="")
    code = models.TextField()
    linenos = models.BooleanField(default=False)
    language = models.CharField(
        choices=LANGUAGE_CHOICES, default="python", max_length=100
    )
    style = models.CharField(choices=STYLE_CHOICES, default="friendly", max_length=100)
    owner = models.ForeignKey(
    "auth.User", related_name="snippets", on_delete=models.CASCADE
    )
    highlighted = models.TextField()
    fuente = models.ForeignKey("book", related_name = "snippets", on_delete=models.CASCADE, blank=True, null=True)
    draft = models.BooleanField(default=True)
    like = models.ManyToManyField("auth.User", related_name="likes", blank=True)

    def save(self, *args, **kwargs):
        """
        Use the `pygments` library to create a highlighted HTML
        representation of the code snippet.
        """
        lexer = get_lexer_by_name(self.language) #obtiene lexer adecuado para el lenguaje que utilizamos
        linenos = "table" if self.linenos else False #decideix si mostrar el nums de linea o no
        options = {"title": self.title} if self.title else {} #si hi ha un titol, l'utilitza com a titol de HTML
        formatter = HtmlFormatter(style=self.style, linenos=linenos, full=True, **options) #cera un formateador html
        self.highlighted = highlight(self.code, lexer, formatter) #converteix el codi en un codi colorejat
        super().save(*args, **kwargs) #guarda l'objecte a la base de dades

        #un lexer transforma una cadena de texto en una secuencia de tokens
        # un token es una unidad minima con significado en un lenguaje
        #un lexer es necesario para identificar que dice el txto y como esta estructurado
        #primera fase de un compilador o intérprete

#select related prefetch related

    def __str__(self):
        return self.title

    class Meta: #configurar comportament classe Snippet
        ordering = ["created"]


class book(models.Model):
    User = get_user_model()
    title = models.CharField(max_length = 100, blank=False)
    author = models.ForeignKey("auth.User", related_name = "books", on_delete=models.CASCADE, default= User.objects.get(username='AnonymousAuthor').pk)
    editorial = models.ForeignKey("editorial", related_name = "books", on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.title    

#no se perquè no acaba de funcionar el OneToOne field
class company(models.Model):
    name = models.CharField(max_length = 100, default = "", blank=True, null=True)
    email = models.EmailField(max_length = 254, null = True)

    def __str__(self):
        return self.name

class editorial(models.Model):
    #company = models.OneToOneField(company, on_delete = models.CASCADE, parent_link= True)
    countries = models.ManyToManyField("country", related_name = "editorials")

    def __str__(self):
        return self.company.name


class opinion(models.Model):
    RATINGS = [
        ("0", 0) , ("1", 1) , ("2", 2) , ("3", 3) , ("4", 4) , ("5", 5) , ("6", 6) , ("7", 7) , ("8", 8) , ("9", 9) , ("10", 10)
    ]
    title = models.CharField(max_length = 50, default = "", blank=True)
    text = models.CharField(max_length =  500, default = "", blank = True)
    rating = models.IntegerField(choices=RATINGS)
    author = models.ForeignKey("auth.User", related_name = "opinions", on_delete = models.CASCADE, null=True)
    book = models.ForeignKey("book", related_name = "opinions", on_delete = models.CASCADE, null = True, blank = True)
    date = models.DateTimeField(auto_now_add=True, null = True)

    def __str__(self):
        return opinion.title

    #related_name és com book veu a opinions, no al revés (serveix per fer les relacions inverses)

class Base(models.Model):
    name = models.CharField(max_length = 50, unique = True)

    class Meta:
        abstract = True

class country(Base):

    def __str__(self):
        return self.name
    
class region(Base):
    country = models.ForeignKey(country, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
class municipality(Base):
    region = models.ForeignKey(region, on_delete=models.CASCADE)

    #class Meta:
    #    abstract = True

    def __str__(self):
        return self.name
    
    class Meta:
        unique_together = ['name', 'region']
    
    
class town (municipality):
    population = models.IntegerField(validators=[MaxValueValidator(9999), MinValueValidator(0)])
    

class city (municipality):
    population = models.IntegerField(validators=[MinValueValidator(10000)])

class Genre(Base):
    description = models.CharField(max_length = 100)

    def __str__(self):
        return self.name
    
class Comment(models.Model):
    text = models.CharField(max_length=100)
    owner = models.ForeignKey("auth.User", related_name= "comments", on_delete=models.CASCADE)
    like = models.ManyToManyField("auth.User", related_name="comment_likes", blank=True)

    def __str__(self):
        return self.text