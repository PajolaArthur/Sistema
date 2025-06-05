from django.db import models
from django.contrib.auth.models import User


# 🔹 Choices
TIPO_PESSOA_CHOICES = [
    ('F', 'Física'),
    ('J', 'Jurídica'),
]


class UF(models.Model):
    nome = models.CharField(max_length=100)
    sigla = models.CharField(max_length=2, unique=True)
    ibge_id = models.IntegerField(unique=True, null=True, blank=True)

    def __str__(self):
        return f'{self.nome} ({self.sigla})'


class Municipio(models.Model):
    nome = models.CharField(max_length=150)
    uf = models.ForeignKey(UF, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('nome', 'uf')

    def __str__(self):
        return f'{self.nome} - {self.uf.sigla}'


# 🔹 Cliente
class Cliente(models.Model):
    nome_razao = models.CharField('Nome/Razão Social', max_length=255)
    tipo_pessoa = models.CharField('Tipo de Pessoa', max_length=1, choices=[('F', 'Física'), ('J', 'Jurídica')])
    cpf_cnpj = models.CharField('CPF/CNPJ', max_length=18, unique=True)
    ie_rg = models.CharField('IE/RG', max_length=20, blank=True, null=True)
    email = models.EmailField('Email', blank=True, null=True)
    telefone = models.CharField('Telefone', max_length=20, blank=True, null=True)
    celular = models.CharField('Celular', max_length=20, blank=True, null=True)

    cep = models.CharField('CEP', max_length=9, blank=True, null=True)
    logradouro = models.CharField('Logradouro', max_length=255, blank=True, null=True)
    numero = models.CharField('Número', max_length=20, blank=True, null=True)
    complemento = models.CharField('Complemento', max_length=100, blank=True, null=True)
    bairro = models.CharField('Bairro', max_length=100, blank=True, null=True)

    uf = models.ForeignKey(UF, on_delete=models.SET_NULL, null=True, verbose_name='UF')
    municipio = models.ForeignKey(Municipio, on_delete=models.SET_NULL, null=True, verbose_name='Município')

    observacoes = models.TextField('Observações', blank=True, null=True)
    ativo = models.BooleanField('Ativo', default=True)

    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)
    excluido_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='cliente_excluido_por')
    excluido_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nome_razao']

    def __str__(self):
        return self.nome_razao