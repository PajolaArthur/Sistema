from django import template
from django import template
from models import Formapagamento  # ou o caminho correto do seu model

register = template.Library()

@register.filter
def get(dictionary, key):
    return dictionary.get(key)

@register.filter
def get_display_forma(sigla):
    forma = Formapagamento.objects.filter(sigla=sigla).first()
    return forma.forma if forma else sigla