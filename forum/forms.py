from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegistroUsuarioForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    nome = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    sobrenome = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    data_nascimento = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    cpf = forms.CharField(
        max_length=14,
        label='CPF',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    cep = forms.CharField(
        max_length=9,
        label='CEP',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    endereco = forms.CharField(
        max_length=200,
        label='Endereço',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    telefone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2',
                  'nome', 'sobrenome', 'data_nascimento',
                  'cpf', 'cep', 'endereco', 'telefone']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }
