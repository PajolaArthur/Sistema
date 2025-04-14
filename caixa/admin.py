from django.contrib import admin
from .models import Caixa, Movimento

@admin.register(Caixa)
class CaixaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'abertura_caixa', 'fechamento_caixa')
    list_filter = ('usuario',)
    search_fields = ('usuario__username',)
    date_hierarchy = 'abertura_caixa'

@admin.register(Movimento)
class MovimentoAdmin(admin.ModelAdmin):
    list_display = ('caixa', 'tipo', 'forma', 'valor', 'criado_em', 'usuario')
    list_filter = ('tipo', 'forma')
    search_fields = ('observacao', 'usuario__username')
    date_hierarchy = 'criado_em'
