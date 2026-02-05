from django.contrib import admin
from snippets.models import Snippet, book, country, editorial, opinion

# Register your models here.
admin.site.register(Snippet)
admin.site.register(book)
admin.site.register(editorial)
admin.site.register(country)
admin.site.register(opinion)


# quan busco el /admin no fa res
