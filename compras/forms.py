from django import forms
from .models import Compra 


class CompraForm(forms.ModelForm):
    class Meta: 
        model = Compra
        fields = ['descricao_produto','codigo_produto','codigo_fornecedor','situacao','fabricante_produto','categoria_produto']


class CompraFormCreate(forms.ModelForm):
    class Meta: 
        model = Compra
        fields = ['descricao_produto','codigo_produto','codigo_fornecedor','fabricante_produto','categoria_produto']

