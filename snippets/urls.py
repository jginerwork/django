"""
from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from snippets import views
from rest_framework import renderers
from snippets.views import api_root, SnippetViewSet, UserViewSet

snippet_list = SnippetViewSet.as_view({"get": "list", "post": "create"})
snippet_detail = SnippetViewSet.as_view(
    {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
)
snippet_highlight = SnippetViewSet.as_view(
    {"get": "highlight"}, renderer_classes=[renderers.StaticHTMLRenderer]
)
user_list = UserViewSet.as_view({"get": "list"})
user_detail = UserViewSet.as_view({"get": "retrieve"})

urlpatterns = format_suffix_patterns(
    [
        path("", api_root),
        path("snippets/", snippet_list, name="snippet-list"),
        path("snippets/<int:pk>/", snippet_detail, name="snippet-detail"),
        path(
            "snippets/<int:pk>/highlight/", snippet_highlight, name="snippet-highlight"
        ),
        path("users/", user_list, name="user-list"),
        path("users/<int:pk>/", user_detail, name="user-detail"),
    ]
)
urlpatterns = format_suffix_patterns(urlpatterns) #per a admetre suffixes a les URLs corresponents al format de la informació

urlpatterns += [
    path("api-auth/", include("rest_framework.urls")),
]
"""

#al utilitzar viewsets no cal fer la configuració de les urls de manera manual
#podem fer-la de manera automàtica utilitzant routers
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from snippets import views
from .views import UserRegistrationView
from django.contrib import admin
from .views import view
from .serializers import RegionSerializer
from .models import region
from rest_framework import mixins
from rest_framework import generics

app_name = "snippets"

# Create a router and register our ViewSets with it.
router = DefaultRouter()
router.register(r"snippets", views.SnippetViewSet, basename="snippet")
router.register(r"users", views.UserViewSet, basename="user")
router.register(r"books", views.BookViewSet, basename = "book")
router.register(r"editorial", views.EditorialViewSet, basename = "editorial")
router.register(r"opinion", views.OpinionViewSet, basename = "opinion")
router.register(r"country", views.CountryViewSet, basename = "country")
router.register(r"regions", views.RegionViewSet, basename = "region")
router.register(r"genres", views.GenreViewSet, basename="genre")
router.register(r"comments", views.CommentViewSet, basename="comment")
router.register(r"notifications", views.NotificationViewSet, basename="notification")

#router.register(r"company", views.CompanyViewSet, basename = "company")

# The API URLs are now determined automatically by the router.
urlpatterns = [ 
    path("", include(router.urls)),
    path("register", UserRegistrationView.as_view(), name="user-register"),
    path("view", view, name = 'view'),
    #path("regions/", views.RegionsList.as_view(), name = 'get-regions'),
    #path("region/<str:name>/", views.RegionDetail.as_view(), name = 'get-region-by-name'),
    path("municipalities", views.MunicipalityList.as_view(), name = 'get-municipality'),
    path("city", views.CityList.as_view(), name = 'get-city'),
    path("town", views.TownList.as_view(), name = 'get-town'),
]
