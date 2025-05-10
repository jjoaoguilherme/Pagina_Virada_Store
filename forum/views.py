from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from .forms import RegistroUsuarioForm, PerfilForm
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

@login_required
def editar_perfil(request):
    perfil = get_object_or_404(Perfil, usuario=request.user)

    if request.method == 'POST':
        form = PerfilForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil atualizado com sucesso!")
            return redirect('perfil_usuario')
    else:
        form = PerfilForm(instance=perfil)

    return render(request, 'forum/editar_perfil.html', {'form': form})


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

@login_required
def editar_perfil(request):
    perfil = get_object_or_404(Perfil, usuario=request.user)
    if request.method == 'POST':
        form = PerfilForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('perfil_usuario')
    else:
        form = PerfilForm(instance=perfil)

    return render(request, 'forum/editar_perfil.html', {'form': form})

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
<<<<<<< Updated upstream
    carrinho.pop(str(livro_id), None)
=======

    if str(livro_id) in carrinho:
        del carrinho[str(livro_id)]
        request.session['carrinho'] = carrinho
        messages.success(request, "Livro removido completamente do carrinho.")

    return redirect('carrinho')

# Finalizar compra
def finalizar_compra(request):
    carrinho = request.session.get('carrinho', {})

    if not carrinho:
        messages.error(request, 'Seu carrinho está vazio.')
        return redirect('carrinho')

    # Se o carrinho tem itens, finaliza:
    request.session['carrinho'] = {}
    messages.success(request, 'Compra finalizada com sucesso! Obrigado pela preferência.')
    return redirect('carrinho')

# Adicionar/remover livro da wishlist
@login_required
def toggle_wishlist(request, livro_id):
    livro = get_object_or_404(Livro, id=livro_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, livro=livro)
    if not created:
        wishlist_item.delete()
    return redirect(request.META.get('HTTP_REFERER', 'home'))

# Ver wishlist
@login_required
def wishlist(request):
    desejos = Wishlist.objects.filter(user=request.user)
    return render(request, 'forum/wishlist.html', {'desejos': desejos})
# Confirmar finalização da compra
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .forms import RegistroUsuarioForm
from .models import Perfil, Livro, Categoria, Wishlist

# Registro de usuário
def registrar_usuario(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            if Perfil.objects.filter(cpf=form.cleaned_data['cpf']).exists():
                messages.error(request, 'CPF já cadastrado.')
                return render(request, 'forum/cadastro.html', {'form': form})

            if Perfil.objects.filter(telefone=form.cleaned_data['telefone']).exists():
                messages.error(request, 'Telefone já cadastrado.')
                return render(request, 'forum/cadastro.html', {'form': form})

            if User.objects.filter(username=form.cleaned_data['username']).exists():
                messages.error(request, 'Usuário já cadastrado.')
                return render(request, 'forum/cadastro.html', {'form': form})

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

# Login de usuário
def login_usuario(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, 'Preencha todos os campos.')
            return render(request, 'forum/login.html', {'username': username})

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login realizado com sucesso!')
            return redirect('home')
        else:
            messages.error(request, 'Usuário ou senha incorretos.')
            return render(request, 'forum/login.html', {'username': username})

    return render(request, 'forum/login.html')

# Logout
def logout_usuario(request):
    logout(request)
    messages.success(request, 'Você saiu da conta.')
    return redirect('home')

# Página inicial
def home(request):
    livros = Livro.objects.all()
    mais_vendidos = Livro.objects.order_by('-vendas')[:10]
    recomendados = Livro.objects.filter(recomendado=True)[:10]
    desejos_count = Wishlist.objects.filter(user=request.user).count() if request.user.is_authenticated else 0
    context = {
        'livros': livros,
        'mais_vendidos': mais_vendidos,
        'recomendados': recomendados,
        'desejos_count': desejos_count,
        'categorias': Categoria.objects.all(),
    }
    return render(request, 'forum/home.html', context)

# Categorias
def categorias(request):
    categorias = Categoria.objects.prefetch_related('livros').all()
    return render(request, 'forum/categorias.html', {'categorias': categorias})

# Mais vendidos
def mais_vendidos(request):
    livros = Livro.objects.order_by('-vendas')[:10]
    return render(request, 'forum/mais_vendidos.html', {'livros': livros})

# Recomendados
def ver_recomendados(request):
    livros = Livro.objects.filter(recomendado=True)
    return render(request, 'forum/recomendados.html', {'livros': livros})

from .models import Wishlist

from django.shortcuts import render, get_object_or_404
from .models import Livro, Wishlist

def detalhes_livro(request, livro_id):
    livro = get_object_or_404(Livro, id=livro_id)

    is_in_wishlist = False
    if request.user.is_authenticated:
        is_in_wishlist = Wishlist.objects.filter(user=request.user, livro=livro).exists()

    return render(request, 'forum/detalhes_livro.html', {
        'livro': livro,
        'is_in_wishlist': is_in_wishlist,  # <-- passa essa variável para o template
    })

# Buscar livros
def buscar_livros(request):
    query = request.GET.get('q')
    resultados = []

    if query:
        resultados = Livro.objects.filter(
            Q(titulo__icontains=query) |
            Q(autor__icontains=query) |
            Q(categoria__nome__icontains=query)
        )
        if not resultados.exists():
            mensagem = "Desculpe, não encontramos resultados para sua pesquisa."
            return render(request, 'forum/buscar.html', {'mensagem': mensagem, 'query': query})
    else:
        mensagem = "Por favor, insira um termo para buscar."
        return render(request, 'forum/buscar.html', {'mensagem': mensagem})

    return render(request, 'forum/buscar.html', {'resultados': resultados, 'query': query})

# Carrinho de compras
def carrinho(request):
    carrinho = request.session.get('carrinho', {})
    livros = []
    total = 0

    for livro_id, quantidade in carrinho.items():
        try:
            livro = Livro.objects.get(id=livro_id)
            subtotal = livro.preco * quantidade
            total += subtotal
            livros.append({
                'livro': livro,
                'quantidade': quantidade,
                'subtotal': subtotal,
            })
        except Livro.DoesNotExist:
            continue

    return render(request, 'forum/carrinho.html', {
        'livros': livros,
        'total': total,
    })

# Adicionar ao carrinho
from django.http import JsonResponse

def adicionar_ao_carrinho(request, livro_id):
    carrinho = request.session.get('carrinho', {})
    carrinho[str(livro_id)] = carrinho.get(str(livro_id), 0) + 1
>>>>>>> Stashed changes
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

# ------------------------ MEUS PEDIDOS ------------------------

@login_required
def meus_pedidos(request):
    # Aqui você pode integrar com um modelo de pedidos real, se quiser
    return render(request, 'forum/meus_pedidos.html')

# ------------------------ PÁGINA DE AGRADECIMENTO ------------------------

@login_required
def obrigado(request):
    return render(request, 'forum/obrigado.html')

@login_required
def rastrear_pedido(request, pedido_id):
    from .models import Pedido, EventoPedido  # ou coloque no topo se preferir

    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    eventos = EventoPedido.objects.filter(pedido=pedido).order_by('-data')

    return render(request, 'forum/rastrear_pedido.html', {
        'pedido': pedido,
        'eventos': eventos,
    })

<<<<<<< Updated upstream
=======
def livros_por_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, pk=categoria_id)
    livros = Livro.objects.filter(categoria=categoria).order_by('-id')  # padrão: mais recentes
    return render(request, 'forum/categoria_detalhe.html', {
        'categoria': categoria,
        'livros': livros,
    })

>>>>>>> Stashed changes
