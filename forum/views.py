from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from .forms import RegistroUsuarioForm
from .models import Perfil, Livro, Categoria, Wishlist

# ------------------------ AUTENTICAÇÃO ------------------------

def registrar_usuario(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            if Perfil.objects.filter(cpf=form.cleaned_data['cpf']).exists():
                messages.error(request, 'CPF já cadastrado.')
            elif Perfil.objects.filter(telefone=form.cleaned_data['telefone']).exists():
                messages.error(request, 'Telefone já cadastrado.')
            elif User.objects.filter(username=form.cleaned_data['username']).exists():
                messages.error(request, 'Usuário já cadastrado.')
            else:
                with transaction.atomic():
                    usuario = form.save()
                    Perfil.objects.create(
                        usuario=usuario,
                        nome=form.cleaned_data['nome'],
                        sobrenome=form.cleaned_data['sobrenome'],
                        tipo_pessoa=form.cleaned_data['tipo_pessoa'],
                        data_nascimento=form.cleaned_data['data_nascimento'],
                        cpf=form.cleaned_data['cpf'],
                        cep=form.cleaned_data['cep'],
                        endereco=form.cleaned_data['endereco'],
                        telefone=form.cleaned_data['telefone'],
                    )
                messages.success(request, 'Cadastro realizado com sucesso! Faça login.')
                return redirect('login')
        else:
            messages.error(request, 'Erro ao cadastrar. Verifique os dados.')
    else:
        form = RegistroUsuarioForm()

    return render(request, 'forum/cadastro.html', {'form': form})

def login_usuario(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not username or not password:
            messages.error(request, 'Preencha todos os campos.')
        else:
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, 'Login realizado com sucesso!')
                return redirect('home')
            else:
                messages.error(request, 'Usuário ou senha incorretos.')

    return render(request, 'forum/login.html')

def logout_usuario(request):
    logout(request)
    messages.success(request, 'Você saiu da conta.')
    return redirect('home')

# ------------------------ PÁGINAS PÚBLICAS ------------------------

def home(request):
    livros = Livro.objects.all()
    mais_vendidos = Livro.objects.order_by('-vendas')[:10]
    recomendados = Livro.objects.filter(recomendado=True)[:10]
    desejos_count = Wishlist.objects.filter(user=request.user).count() if request.user.is_authenticated else 0
    return render(request, 'forum/home.html', {
        'livros': livros,
        'mais_vendidos': mais_vendidos,
        'recomendados': recomendados,
        'desejos_count': desejos_count,
    })

def categorias(request):
    categorias = Categoria.objects.prefetch_related('livros').all()
    return render(request, 'forum/categorias.html', {'categorias': categorias})

def mais_vendidos(request):
    livros = Livro.objects.order_by('-vendas')[:10]
    return render(request, 'forum/mais_vendidos.html', {'livros': livros})

def ver_recomendados(request):
    livros = Livro.objects.filter(recomendado=True)
    return render(request, 'forum/recomendados.html', {'livros': livros})

def detalhes_livro(request, livro_id):
    livro = get_object_or_404(Livro, id=livro_id)
    is_in_wishlist = request.user.is_authenticated and Wishlist.objects.filter(user=request.user, livro=livro).exists()
    return render(request, 'forum/detalhes_livro.html', {'livro': livro, 'is_in_wishlist': is_in_wishlist})

def buscar_livros(request):
    query = request.GET.get('q')
    if not query:
        return render(request, 'forum/buscar.html', {'mensagem': 'Por favor, insira um termo para buscar.'})

    resultados = Livro.objects.filter(
        Q(titulo__icontains=query) |
        Q(autor__icontains=query) |
        Q(categoria__nome__icontains=query)
    )
    if not resultados.exists():
        return render(request, 'forum/buscar.html', {'mensagem': 'Desculpe, nenhum resultado encontrado.', 'query': query})

    return render(request, 'forum/buscar.html', {'resultados': resultados, 'query': query})

@login_required
def perfil_usuario(request):
    perfil = get_object_or_404(Perfil, usuario=request.user)
    return render(request, 'forum/perfil.html', {'perfil': perfil})


# ------------------------ CARRINHO ------------------------

def carrinho(request):
    carrinho = request.session.get('carrinho', {})
    livros, total = [], 0
    for livro_id, quantidade in carrinho.items():
        try:
            livro = Livro.objects.get(id=livro_id)
            subtotal = livro.preco * quantidade
            total += subtotal
            livros.append({'livro': livro, 'quantidade': quantidade, 'subtotal': subtotal})
        except Livro.DoesNotExist:
            continue
    return render(request, 'forum/carrinho.html', {'livros': livros, 'total': total})

def adicionar_ao_carrinho(request, livro_id):
    carrinho = request.session.get('carrinho', {})
    carrinho[str(livro_id)] = carrinho.get(str(livro_id), 0) + 1
    request.session['carrinho'] = carrinho

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        total_itens = sum(carrinho.values())
        return JsonResponse({'mensagem': 'Livro adicionado com sucesso!', 'total_itens': total_itens})

    return redirect('carrinho')

def remover_do_carrinho(request, livro_id):
    carrinho = request.session.get('carrinho', {})
    livro_id_str = str(livro_id)
    if livro_id_str in carrinho:
        carrinho[livro_id_str] = carrinho[livro_id_str] - 1 if carrinho[livro_id_str] > 1 else 0
        if carrinho[livro_id_str] <= 0:
            del carrinho[livro_id_str]
        request.session['carrinho'] = carrinho
        messages.success(request, 'Livro removido do carrinho.')
    return redirect('carrinho')

def remover_todos_do_carrinho(request, livro_id):
    carrinho = request.session.get('carrinho', {})
    carrinho.pop(str(livro_id), None)
    request.session['carrinho'] = carrinho
    messages.success(request, "Livro removido completamente do carrinho.")
    return redirect('carrinho')

# ------------------------ FINALIZAÇÃO ------------------------

@login_required
def finalizar_compra(request):
    carrinho = request.session.get('carrinho', {})
    if not carrinho:
        messages.error(request, 'Seu carrinho está vazio.')
        return redirect('carrinho')

    request.session['carrinho'] = {}
    messages.success(request, 'Compra finalizada com sucesso! Obrigado pela preferência.')
    return redirect('carrinho')

@login_required
def confirmar_finalizacao(request):
    carrinho = request.session.get('carrinho', {})
    if not carrinho:
        messages.error(request, "Seu carrinho está vazio.")
        return redirect('carrinho')

    livros, total = [], 0
    for livro_id, quantidade in carrinho.items():
        try:
            livro = Livro.objects.get(id=livro_id)
            subtotal = livro.preco * quantidade
            total += subtotal
            livros.append({'livro': livro, 'quantidade': quantidade, 'subtotal': subtotal})
        except Livro.DoesNotExist:
            continue

    return render(request, 'forum/confirmar_finalizacao.html', {'livros': livros, 'total': total})

@login_required
def checkout(request):
    carrinho = request.session.get('carrinho', {})
    if not carrinho:
        messages.error(request, 'Seu carrinho está vazio.')
        return redirect('carrinho')

    livros, total = [], 0
    for livro_id, quantidade in carrinho.items():
        try:
            livro = Livro.objects.get(id=livro_id)
            subtotal = livro.preco * quantidade
            total += subtotal
            livros.append({'livro': livro, 'quantidade': quantidade, 'subtotal': subtotal})
        except Livro.DoesNotExist:
            continue

    if request.method == 'POST' and 'forma_pagamento' in request.POST:
        request.session['carrinho'] = {}
        messages.success(request, 'Compra finalizada com sucesso!')
        return render(request, 'forum/obrigado.html')

    return render(request, 'forum/checkout.html', {'livros': livros, 'total': total})

# ------------------------ WISHLIST ------------------------

@login_required
def toggle_wishlist(request, livro_id):
    livro = get_object_or_404(Livro, id=livro_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, livro=livro)
    if not created:
        wishlist_item.delete()
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def wishlist(request):
    desejos = Wishlist.objects.filter(user=request.user)
    return render(request, 'forum/wishlist.html', {'desejos': desejos})
