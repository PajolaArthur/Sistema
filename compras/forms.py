from django import forms
from .models import Compra 
from django import forms
from .models import Fabricante
from .models import Categoria


class CompraForm(forms.ModelForm):
    class Meta: 
        model = Compra
        fields = ['descricao_produto','codigo_produto','codigo_fornecedor','situacao','fabricante_produto','categoria_produto']


class CompraFormCreate(forms.ModelForm):
    class Meta: 
        model = Compra
        fields = ['descricao_produto','codigo_produto','codigo_fornecedor','fabricante_produto','categoria_produto']


class FabricanteForm(forms.ModelForm):
    class Meta:
        model = Fabricante
        fields = ['sigla', 'nome']

class FabricanteForm(forms.ModelForm):
    class Meta:
        model = Fabricante
        fields = ['nome', 'sigla']
        
class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome', 'sigla']
