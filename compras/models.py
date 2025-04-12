from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

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
        ('GIG','GIGA'),
        ('MKN','MKN'),
        ('MCM','MCM'),
        ('AGL','AGL'),
        ('FC','FONTE CFTV'),
        ('TEM','TEM'),
        ('OUT','OUTROS')
    ]

    CATEGORIAS = [
        ('MOT','MOTOR'),
        ('CEN','CENTRAL'),
        ('CAM','CAMERA'),
        ('PEÇ','PEÇA'),
        ('DVR','DVR'),
        ('FON','FONTE'),
        ('SEN','SENSOR'),
        ('OUT','OUTROS')
    ]

    descricao_produto = models.CharField(max_length=255)
    codigo_produto = models.CharField(max_length=4)
    codigo_fornecedor = models.CharField(max_length=16, blank=True, null=True)
    fabricante_produto = models.CharField(max_length=20,choices=FABRICANTES, default='NIF')
    categoria_produto = models.CharField(max_length=20, choices=CATEGORIAS, default='NIF')
    situacao = models.CharField(max_length=1,choices=COMPRA_STATUS, default='P')
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    excluido_em = models.DateTimeField(null=True, blank=True, default=None)
     

    @property
    def dias_desde_criacao(self):
        criado_em_local = timezone.localtime(self.criado_em).date()
        hoje_local = timezone.localdate()
        return (hoje_local - criado_em_local).days

    def __str__(self):
        return self.descricao_produto