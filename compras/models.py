from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Fabricante(models.Model):
    nome = models.CharField(max_length=50, unique=True)
    sigla = models.CharField(max_length=10, unique=True)
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    excluido_por = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='fabricantes_excluidos')
    excluido_em = models.DateTimeField(null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.sigla} - {self.nome}"

class Categoria(models.Model):
    nome = models.CharField(max_length=50, unique=True)
    sigla = models.CharField(max_length=10, unique=True)
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    excluido_por = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='categorias_excluidas')
    excluido_em = models.DateTimeField(null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.sigla} - {self.nome}"


    def __str__(self):
        return f"{self.sigla} - {self.nome}"

class Compra(models.Model):
    COMPRA_STATUS = [
        ('P','Pendente'),
        ('A','Aprovado'),
        ('R','Recusado'),
        ('C','Concluído')
    ]

    descricao_produto = models.CharField(max_length=255)
    codigo_produto = models.CharField(max_length=4)
    codigo_fornecedor = models.CharField(max_length=16, blank=True, null=True)
    fabricante_produto = models.ForeignKey(Fabricante, on_delete=models.SET_NULL, null=True, blank=True)
    categoria_produto = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    situacao = models.CharField(max_length=1,choices=COMPRA_STATUS, default='P')
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    excluido_por = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='compras_excluidas')
    excluido_em = models.DateTimeField(null=True, blank=True, default=None)
     

    @property
    def dias_desde_criacao(self):
        criado_em_local = timezone.localtime(self.criado_em).date()
        hoje_local = timezone.localdate()
        return (hoje_local - criado_em_local).days

    def __str__(self):
        return self.descricao_produto
    
    
