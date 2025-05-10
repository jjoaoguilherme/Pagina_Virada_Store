from django.contrib import admin
from .models import Livro, Categoria, Perfil, Wishlist

@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'preco', 'recomendado')  # Adiciona coluna "Recomendado" no admin
    list_filter = ('recomendado', 'categoria')  # Filtro lateral por recomendado e categoria
    search_fields = ('titulo', 'autor')  # Caixa de busca no admin
    list_editable = ('recomendado',)  # Permite editar "recomendado" direto da lista

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    search_fields = ('nome',)

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    search_fields = ('nome', 'sobrenome', 'cpf')

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'livro')
    search_fields = ('user__username', 'livro__titulo')
from django.contrib import admin
from .models import Pedido, ItemPedido

class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    readonly_fields = ('livro', 'quantidade', 'subtotal')

class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total', 'criado_em')
    list_filter = ('criado_em',)
    search_fields = ('user__username',)
    inlines = [ItemPedidoInline]
    ordering = ('-criado_em',)

admin.site.register(Pedido, PedidoAdmin)
