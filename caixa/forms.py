from django import forms
from .models import Movimento
from django.utils import timezone
from django.contrib.auth.models import User

class MovimentoConsultaForm(forms.Form):
    data_inicio = forms.DateField(
        label='Data Início',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=timezone.now().date()  # Valor inicial para data de hoje
    )
    data_fim = forms.DateField(
        label='Data Final',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=timezone.now().date()  # Valor inicial para data de hoje
    )
    tipo = forms.ChoiceField(
        label='Tipo',
        choices=[('', 'Todos')] + list(Movimento.TIPO_MOVIMENTO),
        required=False
    )
    forma = forms.ChoiceField(
        label='Forma de Pagamento',
        choices=[('', 'Todas')] + list(Movimento.FORMAS_PAGAMENTO),
        required=False
    )
    usuario = forms.ModelChoiceField(
        label='Usuário',
        queryset=User.objects.all(),
        required=False,
        empty_label='Todos'
    )
