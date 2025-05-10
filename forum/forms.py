from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Perfil

class RegistroUsuarioForm(UserCreationForm):
    TIPO_PESSOA_CHOICES = [
        ('Física', 'Pessoa Física'),
        ('Jurídica', 'Pessoa Jurídica'),
    ]

    tipo_pessoa = forms.ChoiceField(choices=TIPO_PESSOA_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    nome = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    sobrenome = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    data_nascimento = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    cpf = forms.CharField(max_length=14, widget=forms.TextInput(attrs={'class': 'form-control'}))
    cep = forms.CharField(max_length=9, widget=forms.TextInput(attrs={'class': 'form-control'}))
    endereco = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
    telefone = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'tipo_pessoa', 'nome', 'sobrenome', 'data_nascimento', 'cpf', 'cep', 'endereco', 'telefone']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

from django import forms
from .models import Perfil

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['nome', 'sobrenome', 'telefone', 'cep', 'endereco']
