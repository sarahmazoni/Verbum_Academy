from django.urls import path

from . import views


urlpatterns = [
    path(
        "",
        views.homePage,
        name="homePage"
    ),

    path(
        "register/",
        views.register_page,
        name="register"
    ),

    path(
        "vocabulario/",
        views.vocabulario,
        name="vocabulario"
    ),

    path(
        "chunks/",
        views.chunks,
        name="chunks"
    ),

	path(
        "espanhol/vocabulario/",
        views.vocabulario_espanhol,
        name="vocabulario_espanhol"
    ),

    path(
        "espanhol/chunks/",
        views.chunks_espanhol,
        name="chunks_espanhol"
    ),
]