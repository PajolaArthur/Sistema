from django import template
from caixa.models import Movimento

register = template.Library()

@register.filter
def get_display_forma(value):
    for code, name in Movimento.FORMAS_PAGAMENTO:
        if code == value:
            return name
    return value