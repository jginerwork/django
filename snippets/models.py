from django.db import models
#pygments: libreria de resaltado de sintaxis
from pygments.lexers import get_all_lexers #devulve todos los lenguajes de programación reconocidos por pygments
from pygments.styles import get_all_styles #devuelve todos los estilos de colores utilizados por pygments para resaltar codigo
from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import HtmlFormatter
from pygments import highlight

LEXERS = [item for item in get_all_lexers() if item[1]] #devuelve los lenguajes con un alias (?)
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS]) #devuelve lista de tuplas (alias_lenguaje, nombre_lenguaje)
STYLE_CHOICES = sorted([(item, item) for item in get_all_styles()]) #lista tuplas estilos disponibles

#util para en un formulario desplegar select de todos los lenguajes y estilos disponibles

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

    class Meta: #configurar comportament classe Snippet
        ordering = ["created"]

