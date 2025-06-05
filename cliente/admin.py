from django.contrib import admin
from .models import UF, Municipio, Cliente


@admin.register(UF)
class UFAdmin(admin.ModelAdmin):
    list_display = ('sigla', 'nome')
    search_fields = ('sigla', 'nome')
    ordering = ('sigla',)


@admin.register(Municipio)
class MunicipioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'uf')
    search_fields = ('nome',)
    list_filter = ('uf',)
    ordering = ('nome',)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome_razao', 'tipo_pessoa', 'cpf_cnpj', 'telefone', 'celular', 'municipio', 'uf', 'ativo')
    search_fields = ('nome_razao', 'cpf_cnpj', 'telefone', 'celular')
    list_filter = ('tipo_pessoa', 'uf', 'municipio', 'ativo')
    ordering = ('nome_razao',)

    readonly_fields = ('criado_em', 'atualizado_em', 'criado_por', 'excluido_por', 'excluido_em')

    fieldsets = (
        ('Dados Principais', {
            'fields': (
                'nome_razao',
                ('tipo_pessoa', 'cpf_cnpj', 'ie_rg'),
                ('telefone', 'celular'),
                'email',
                'observacoes',
                'ativo',
            )
        }),
        ('Endereço', {
            'fields': (
                ('cep', 'logradouro', 'numero'),
                ('complemento', 'bairro'),
                ('uf', 'municipio'),
            )
        }),
        ('Controle', {
            'fields': (
                ('criado_por', 'criado_em'),
                ('atualizado_em',),
                ('excluido_por', 'excluido_em'),
            )
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)
