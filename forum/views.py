from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PerfilForm, RegistroUsuarioForm
from .models import Categoria, EventoPedido, Livro, Pedido, Perfil, Wishlist

# ---------------------------------------------------------------------------
# AUTENTICAÇÃO
# ---------------------------------------------------------------------------

def registrar_usuario(request):
    """Cadastro de novo usuário + criação automática de Perfil."""
    form = RegistroUsuarioForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        # Validações de unicidade manuais (username já é validado pelo próprio form)
        if Perfil.objects.filter(cpf=form.cleaned_data["cpf"]).exists():
            messages.error(request, "CPF já cadastrado.")
        elif Perfil.objects.filter(telefone=form.cleaned_data["telefone"]).exists():
            messages.error(request, "Telefone já cadastrado.")
        elif User.objects.filter(username=form.cleaned_data["username"]).exists():
            messages.error(request, "Usuário já cadastrado.")
        else:
            with transaction.atomic():
                usuario = form.save()
                Perfil.objects.create(
                    usuario=usuario,
                    nome=form.cleaned_data["nome"],
                    sobrenome=form.cleaned_data["sobrenome"],
                    tipo_pessoa=form.cleaned_data["tipo_pessoa"],
                    data_nascimento=form.cleaned_data["data_nascimento"],
                    cpf=form.cleaned_data["cpf"],
                    cep=form.cleaned_data["cep"],
                    endereco=form.cleaned_data["endereco"],
                    telefone=form.cleaned_data["telefone"],
                )
            messages.success(request, "Cadastro realizado com sucesso! Faça login.")
            return redirect("login")
    elif request.method == "POST":
        messages.error(request, "Erro ao cadastrar. Verifique os dados.")

    return render(request, "forum/cadastro.html", {"form": form})


def login_usuario(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if not (username and password):
            messages.error(request, "Preencha todos os campos.")
        else:
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, "Login realizado com sucesso!")
                return redirect("home")
            messages.error(request, "Usuário ou senha incorretos.")
    return render(request, "forum/login.html")


def logout_usuario(request):
    logout(request)
    messages.success(request, "Você saiu da conta.")
    return redirect("home")


# ---------------------------------------------------------------------------
# PERFIL
# ---------------------------------------------------------------------------

@login_required
def perfil_usuario(request):
    perfil = get_object_or_404(Perfil, usuario=request.user)
    return render(request, "forum/perfil.html", {"perfil": perfil})


@login_required
def editar_perfil(request):
    perfil = get_object_or_404(Perfil, usuario=request.user)
    form = PerfilForm(request.POST or None, instance=perfil)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Perfil atualizado com sucesso!")
        return redirect("perfil_usuario")
    return render(request, "forum/editar_perfil.html", {"form": form})


# ---------------------------------------------------------------------------
# PÁGINAS PÚBLICAS
# ---------------------------------------------------------------------------

def home(request):
    context = {
        "livros": Livro.objects.all(),
        "mais_vendidos": Livro.objects.order_by("-vendas")[:10],
        "recomendados": Livro.objects.filter(recomendado=True)[:10],
        "desejos_count": Wishlist.objects.filter(user=request.user).count()
        if request.user.is_authenticated else 0,
        "categorias": Categoria.objects.all(),
    }
    return render(request, "forum/home.html", context)


def categorias(request):
    categorias_qs = Categoria.objects.prefetch_related("livros").all()
    return render(request, "forum/categorias.html", {"categorias": categorias_qs})


def livros_por_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, pk=categoria_id)
    livros = Livro.objects.filter(categoria=categoria).order_by("-id")
    return render(
        request,
        "forum/categoria_detalhe.html",
        {"categoria": categoria, "livros": livros},
    )


def mais_vendidos(request):
    return render(
        request, "forum/mais_vendidos.html", {"livros": Livro.objects.order_by("-vendas")[:10]}
    )


def ver_recomendados(request):
    return render(
        request, "forum/recomendados.html", {"livros": Livro.objects.filter(recomendado=True)}
    )


def detalhes_livro(request, livro_id):
    livro = get_object_or_404(Livro, id=livro_id)
    is_in_wishlist = request.user.is_authenticated and Wishlist.objects.filter(
        user=request.user, livro=livro
    ).exists()
    return render(
        request,
        "forum/detalhes_livro.html",
        {"livro": livro, "is_in_wishlist": is_in_wishlist},
    )


def buscar_livros(request):
    query = request.GET.get("q", "")
    if not query:
        return render(request, "forum/buscar.html", {"mensagem": "Por favor, insira um termo para buscar."})

    resultados = Livro.objects.filter(
        Q(titulo__icontains=query) | Q(autor__icontains=query) | Q(categoria__nome__icontains=query)
    )
    if not resultados.exists():
        return render(
            request,
            "forum/buscar.html",
            {"mensagem": "Desculpe, nenhum resultado encontrado.", "query": query},
        )
    return render(request, "forum/buscar.html", {"resultados": resultados, "query": query})


# ---------------------------------------------------------------------------
# CARRINHO
# ---------------------------------------------------------------------------

def _calcula_carrinho(session):
    """Helper para transformar dict do carrinho em lista de itens + total."""
    livros, total = [], 0
    for livro_id, quantidade in session.get("carrinho", {}).items():
        try:
            livro = Livro.objects.get(id=livro_id)
        except Livro.DoesNotExist:
            continue
        subtotal = livro.preco * quantidade
        total += subtotal
        livros.append({"livro": livro, "quantidade": quantidade, "subtotal": subtotal})
    return livros, total


def carrinho(request):
    livros, total = _calcula_carrinho(request.session)
    return render(request, "forum/carrinho.html", {"livros": livros, "total": total})


def adicionar_ao_carrinho(request, livro_id):
    carrinho = request.session.get("carrinho", {})
    carrinho[str(livro_id)] = carrinho.get(str(livro_id), 0) + 1
    request.session["carrinho"] = carrinho

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"mensagem": "Livro adicionado com sucesso!", "total_itens": sum(carrinho.values())})
    return redirect("carrinho")


def remover_do_carrinho(request, livro_id):
    carrinho = request.session.get("carrinho", {})
    key = str(livro_id)
    if key in carrinho:
        carrinho[key] -= 1
        if carrinho[key] <= 0:
            del carrinho[key]
        request.session["carrinho"] = carrinho
        messages.success(request, "Livro removido do carrinho.")
    return redirect("carrinho")


def remover_todos_do_carrinho(request, livro_id):
    carrinho = request.session.get("carrinho", {})
    carrinho.pop(str(livro_id), None)
    request.session["carrinho"] = carrinho
    messages.success(request, "Livro removido completamente do carrinho.")
    return redirect("carrinho")


# ---------------------------------------------------------------------------
# FINALIZAÇÃO / CHECKOUT
# ---------------------------------------------------------------------------

@login_required
def confirmar_finalizacao(request):
    livros, total = _calcula_carrinho(request.session)
    if not livros:
        messages.error(request, "Seu carrinho está vazio.")
        return redirect("carrinho")
    return render(request, "forum/confirmar_finalizacao.html", {"livros": livros, "total": total})


@login_required
def checkout(request):
    livros, total = _calcula_carrinho(request.session)
    if not livros:
        messages.error(request, "Seu carrinho está vazio.")
        return redirect("carrinho")

    if request.method == "POST" and "forma_pagamento" in request.POST:
        # Aqui: processa pagamento, cria Pedido etc.
        request.session["carrinho"] = {}
        messages.success(request, "Compra finalizada com sucesso!")
        return render(request, "forum/obrigado.html")

    return render(request, "forum/checkout.html", {"livros": livros, "total": total})


@login_required
def finalizar_compra(request):
    # Fluxo simples (sem tela intermediária): limpa carrinho e redireciona
    request.session["carrinho"] = {}
    messages.success(request, "Compra finalizada com sucesso! Obrigado pela preferência.")
    return redirect("carrinho")


# ---------------------------------------------------------------------------
# WISHLIST
# ---------------------------------------------------------------------------

@login_required
def toggle_wishlist(request, livro_id):
    livro = get_object_or_404(Livro, id=livro_id)
    item, created = Wishlist.objects.get_or_create(user=request.user, livro=livro)
    if not created:
        item.delete()
    return redirect(request.META.get("HTTP_REFERER", "home"))


@login_required
def wishlist(request):
    return render(request, "forum/wishlist.html", {"desejos": Wishlist.objects.filter(user=request.user)})


# ---------------------------------------------------------------------------
# PEDIDOS / RASTREAMENTO
# ---------------------------------------------------------------------------

@login_required
def meus_pedidos(request):
    pedidos = Pedido.objects.filter(usuario=request.user)
    return render(request, "forum/meus_pedidos.html", {"pedidos": pedidos})


@login_required
def rastrear_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    eventos = EventoPedido.objects.filter(pedido=pedido).order_by("-data")
    return render(request, "forum/rastrear_pedido.html", {"pedido": pedido, "eventos": eventos})


# ---------------------------------------------------------------------------
# PÁGINA DE AGRADECIMENTO (simples)
# ---------------------------------------------------------------------------

@login_required
def obrigado(request):
    return render(request, "forum/obrigado.html")
