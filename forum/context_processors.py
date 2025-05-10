# forum/context_processors.py

def cart_item_count(request):
    """
    Lê exatamente da chave 'carrinho' da sessão e soma todas as quantidades.
    """
    carrinho = request.session.get('carrinho', {})
    total = sum(carrinho.values())
    return {'cart_item_count': total}
