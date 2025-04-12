from django import forms
from .models import Caixa 

class CaixaFormCreate(forms.ModelForm):
    class Meta: 
        model = Caixa
        fields = ['abertura_caixa','fechamento_caixa','usuario']