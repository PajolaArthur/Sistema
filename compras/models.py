from django.db import models
from django.utils import timezone

class Compra(models.Model):
    COMPRA_STATUS = [
        ('P','Pendente'),
        ('A','Aprovado'),
        ('R','Recusado'),
        ('C','Concluído')
    ]

    FABRICANTES = [
        ('PPA','PPA'),
        ('ACT','ACTON'),
        ('HIK','HIKVISION'),
        ('MKN','MKN'),
        ('AGL','AGL'),
        ('NIF','NÃO INFORMADO')
    ]

    CATEGORIAS = [
        ('MOT','MOTOR'),
        ('CEN','CENTRAL'),
        ('CAM','CAMERA'),
        ('PEÇ','PEÇA'),
        ('DVR','DVR'),
        ('NIF','NÃO INFORMADO')
    ]

    descricao_produto = models.CharField(max_length=255)
    codigo_produto = models.CharField(max_length=4)
    codigo_fornecedor = models.CharField(max_length=16)
    fabricante_produto = models.CharField(max_length=20,choices=FABRICANTES, default='NIF')
    categoria_produto = models.CharField(max_length=20, choices=CATEGORIAS, default='NIF')
    situacao = models.CharField(max_length=1,choices=COMPRA_STATUS, default='P')
    criado_em = models.DateTimeField(auto_now_add=True)

    @property
    def dias_desde_criacao(self):
        criado_em_local = timezone.localtime(self.criado_em).date()
        hoje_local = timezone.localdate()
        return (hoje_local - criado_em_local).days

    def __str__(self):
        return self.descricao_produto



    # ID, Descrição, Código Fornecedor, Código Produto, Data, Usuário