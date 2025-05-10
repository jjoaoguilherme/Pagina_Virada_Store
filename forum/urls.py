from django.urls import path
from . import views

urlpatterns = [
    # Página inicial
    path('', views.home, name='home'),

    # Livros e Categorias
    path('categorias/', views.categorias, name='categorias'),
    path('mais-vendidos/', views.mais_vendidos, name='mais_vendidos'),
    path('recomendados/', views.ver_recomendados, name='ver_recomendados'),
    path('<int:livro_id>/', views.detalhes_livro, name='detalhes_livro'),

    # Usuário
    path('registrar/', views.registrar_usuario, name='registrar'),
    path('login/', views.login_usuario, name='login'),
    path('logout/', views.logout_usuario, name='logout'),
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),


    # Carrinho
    path('carrinho/', views.carrinho, name='carrinho'),
    path('adicionar-ao-carrinho/<int:livro_id>/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),
    path('remover-do-carrinho/<int:livro_id>/', views.remover_do_carrinho, name='remover_do_carrinho'),
    path('remover-todos-do-carrinho/<int:livro_id>/', views.remover_todos_do_carrinho, name='remover_todos_do_carrinho'),

    # Finalização de compra
    path('confirmar-finalizacao/', views.confirmar_finalizacao, name='confirmar_finalizacao'),  # página de confirmação
    path('checkout/', views.checkout, name='checkout'),

    # Pesquisa
    path('buscar/', views.buscar_livros, name='buscar_livros'),

    # Wishlist
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/toggle/<int:livro_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    
    path('meus-pedidos/', views.meus_pedidos, name='meus_pedidos'),
    path('obrigado/', views.obrigado, name='obrigado'),
    path('meus-pedidos/<int:pedido_id>/rastrear/', views.rastrear_pedido, name='rastrear_pedido'),

]
