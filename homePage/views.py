from django.shortcuts import render, redirect

from django.contrib import messages
from django.contrib.auth.decorators import login_required

from accounts.models import UserProfile
from accounts.views import login_view

from .vocabulario import PALAVRAS, CHUNKS
from .espanhol import PALAVRAS_ESPANHOL, CHUNKS_ESPANHOL


def homePage(request):

    if request.method == "POST":
        # Encaminha o login da home para o login_view
        return login_view(request)

    return render(request, "login.html")


def register_page(request):
    return redirect("/accounts/register/")


# Verifica se o idioma acessado é o mesmo selecionado no perfil
def idioma_permitido(request, idioma):

    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if profile.study_language != idioma:
        messages.warning(
            request, "Selecione esse idioma no seu perfil para acessar o conteúdo."
        )
        return False

    return True


# VOCABULÁRIO EM INGLÊS


@login_required
def vocabulario(request):

    if not idioma_permitido(request, "en"):
        return redirect("perfil")

    pesquisa = request.GET.get("q", "").strip().casefold()
    categoria = request.GET.get("categoria", "").strip()

    categorias = sorted({palavra["category"] for palavra in PALAVRAS})

    palavras_filtradas = [
        palavra
        for palavra in PALAVRAS
        if (
            not pesquisa
            or pesquisa in palavra["word"].casefold()
            or pesquisa in palavra["translation"].casefold()
        )
        and (not categoria or palavra["category"] == categoria)
    ]

    return render(
        request,
        "vocabulario.html",
        {
            "palavras": palavras_filtradas,
            "categorias": categorias,
            "pesquisa": request.GET.get("q", ""),
            "categoria_selecionada": categoria,
        },
    )


# CHUNKS EM INGLÊS


@login_required
def chunks(request):

    if not idioma_permitido(request, "en"):
        return redirect("perfil")

    pesquisa = request.GET.get("q", "").strip().casefold()
    categoria = request.GET.get("categoria", "").strip()

    categorias = sorted({chunk["category"] for chunk in CHUNKS})

    chunks_filtrados = [
        chunk
        for chunk in CHUNKS if (
            not pesquisa
            or pesquisa in chunk["word"].casefold()
            or pesquisa in chunk["translation"].casefold()
        )
        and (not categoria or chunk["category"] == categoria)
    ]

    return render(
        request,
        "chunks.html",
        {
            "chunks": chunks_filtrados,
            "categorias": categorias,
            "pesquisa": request.GET.get("q", ""),
            "categoria_selecionada": categoria,
        },
    )


# VOCABULÁRIO EM ESPANHOL


@login_required
def vocabulario_espanhol(request):

    if not idioma_permitido(request, "es"):
        return redirect("perfil")

    pesquisa = request.GET.get("q", "").strip().casefold()
    categoria = request.GET.get("categoria", "").strip()

    categorias = sorted({palavra["category"] for palavra in PALAVRAS_ESPANHOL})

    palavras_filtradas = [
        palavra
        for palavra in PALAVRAS_ESPANHOL
        if (
            not pesquisa
            or pesquisa in palavra["word"].casefold()
            or pesquisa in palavra["translation"].casefold()
        )
        and (not categoria or palavra["category"] == categoria)
    ]

    return render(
        request,
        "vocabulario_espanhol.html",
        {
            "palavras": palavras_filtradas,
            "categorias": categorias,
            "pesquisa": request.GET.get("q", ""),
            "categoria_selecionada": categoria,
        },
    )


# CHUNKS EM ESPANHOL


@login_required
def chunks_espanhol(request):

    if not idioma_permitido(request, "es"):
        return redirect("perfil")

    pesquisa = request.GET.get("q", "").strip().casefold()
    categoria = request.GET.get("categoria", "").strip()

    categorias = sorted({chunk["category"] for chunk in CHUNKS_ESPANHOL})

    chunks_filtrados = [
        chunk
        for chunk in CHUNKS_ESPANHOL
        if (
            not pesquisa
            or pesquisa in chunk["word"].casefold()
            or pesquisa in chunk["translation"].casefold()
        )
        and (not categoria or chunk["category"] == categoria)
    ]

    return render(
        request,
        "chunks_espanhol.html",
        {
            "chunks": chunks_filtrados,
            "categorias": categorias,
            "pesquisa": request.GET.get("q", ""),
            "categoria_selecionada": categoria,
        },
    )
