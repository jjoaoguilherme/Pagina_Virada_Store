from django.db import models
from django.contrib.auth.models import User

class Perfil(models.Model):
    TIPO_PESSOA_CHOICES = [
        ('F', 'Pessoa Física'),
        ('J', 'Pessoa Jurídica'),
    ]
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    nome = models.CharField(max_length=100)
    sobrenome = models.CharField(max_length=100)
    tipo_pessoa = models.CharField(max_length=1, choices=TIPO_PESSOA_CHOICES)
    data_nascimento = models.DateField()
    cpf = models.CharField(max_length=14, unique=True)
    cep = models.CharField(max_length=9)
    endereco = models.CharField(max_length=200)
    telefone = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return f"{self.nome} {self.sobrenome}"

class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    imagem = models.URLField(blank=True)

    def __str__(self):
        return self.nome

class Livro(models.Model):
    titulo = models.CharField(max_length=200)
    imagem = models.URLField()
    autor = models.CharField(max_length=100)
    preco = models.DecimalField(max_digits=6, decimal_places=2)
    vendas = models.PositiveIntegerField(default=0)
    recomendado = models.BooleanField(default=False)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='livros', null=True, blank=True)

    def __str__(self):
        return self.titulo

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'livro')

    def __str__(self):
        return f"{self.user.username} deseja {self.livro.titulo}"

class Pedido(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    criado_em = models.DateTimeField(auto_now_add=True)  # ⬅️ NÃO precisa passar manualmente

    def __str__(self):
        return f"Pedido #{self.id} de {self.user.username}"

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='itens', on_delete=models.CASCADE)
    livro = models.ForeignKey(Livro, on_delete=models.PROTECT)
    quantidade = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantidade}x {self.livro.titulo} (Pedido #{self.pedido.id})"

class EventoPedido(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='eventos', on_delete=models.CASCADE)
    data = models.DateField()
    hora = models.TimeField()
    local = models.CharField(max_length=100)
    status = models.CharField(max_length=255)
    detalhes = models.TextField(blank=True, null=True)
